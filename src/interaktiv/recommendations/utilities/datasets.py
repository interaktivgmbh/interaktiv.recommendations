from typing import NoReturn, TypedDict, List

import plone.api as api
from numpy import ndarray
from pandas import DataFrame, Series
from plone.app.contenttypes.content import Folder
from plone.app.textfield.value import RichTextValue
from sklearn.datasets import fetch_20newsgroups
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.interface import Interface


class TNewsGroupData(TypedDict):
    data: List[str]
    filenames: ndarray
    target: ndarray
    target_names: List[str]
    filenames: ndarray


class IDataSetsUtility(Interface):
    """Utility to provide methods for datasets"""


def get_datasets_utility() -> NoReturn:
    return getUtility(IDataSetsUtility)


class DataSetsUtility(object):

    @staticmethod
    def get_dataframe_from_dict_like_data(data: TNewsGroupData, keys: List[str]) -> DataFrame:
        # noinspection PyTypedDict
        processed_dict = {key: data[key] for key in keys}

        return DataFrame.from_dict(processed_dict)

    @staticmethod
    def get_subject(text: str) -> str:
        subject = str()

        for line in text.split('\n'):
            if line.startswith('Subject:'):
                subject = line.replace('Subject:', '', 1).strip()

        return subject

    @staticmethod
    def _validate_line_start(line: str) -> bool:
        bad_starts = [
            'From:',
            'Subject:',
            'Organization:',
            'Lines:',
            'Reply-To:',
            'NNTP-Posting-Host:',
            'Distribution:'
        ]

        for bad_start in bad_starts:
            if line.lower().startswith(bad_start.lower()):
                return False

        return True

    def get_processed_text(self, text: str) -> str:
        lines = list()

        for line in text.split('\n'):
            if not self._validate_line_start(line):
                continue

            line = line.strip()
            if not line:
                continue

            lines.append(line)

        return ' '.join(lines)

    @staticmethod
    def _create_document(container: Folder, _id: str, title: str, text: str) -> NoReturn:
        document = api.content.create(
            container=container,
            type='Document',
            id=_id,
            title=title,
            text=RichTextValue(text)
        )

        api.content.transition(obj=document, transition='publish')
        document.reindexObject()

    @staticmethod
    def _create_document_with_block(container: Folder, _id: str, title: str, text: str) -> NoReturn:
        document = api.content.create(
            container=container,
            type='Document',
            id=_id,
            title=title
        )

        # add block
        text_block_id = 'newsgroup_text'
        recommendations_block_id = 'recommendations'

        blocks = document.blocks.copy()
        blocks[text_block_id] = {
            '@type': 'slate',
            'value': [
                {
                    'type': 'p',
                    'children': [{'text': text}]
                }
            ]
        }
        blocks[recommendations_block_id] = {
            '@type': 'recommendations',
        }
        document.blocks = blocks

        blocks_layout = document.blocks_layout.copy()
        blocks_layout['items'] += [text_block_id, recommendations_block_id]
        document.blocks_layout = blocks_layout

        api.content.transition(obj=document, transition='publish')
        document.reindexObject()

    def _create_plone_content(self, df_data: DataFrame, document_type: str) -> NoReturn:
        portal = api.portal.get()
        chooser = INameChooser(portal)

        # create newsgroup container
        newsgroup_container_id = 'newsgroups'
        newsgroup_container_title = '20 News Groups'
        if newsgroup_container_id not in portal:
            newsgroup_container = api.content.create(
                container=portal,
                type='Folder',
                id=newsgroup_container_id,
                title=newsgroup_container_title
            )
        else:
            newsgroup_container = portal[newsgroup_container_id]

        for index, row in df_data.iterrows():
            print(f'{index}/{len(df_data)}')

            target_id = row['target_name']
            title = row['subject']
            text = row['text']

            if not (target_id and title and text):
                continue

            if target_id in newsgroup_container:
                container = newsgroup_container[target_id]
            else:
                container = api.content.create(
                    container=newsgroup_container,
                    type='Folder',
                    id=target_id,
                    title=target_id
                )

            # noinspection PyArgumentList
            _id = chooser.chooseName(title, portal)
            if _id in container:
                continue

            if document_type == 'block':
                self._create_document_with_block(container, _id, title, text)
            else:
                self._create_document(container, _id, title, text)

    def import_20newsgroups_dataset(self, document_type: str = 'classic') -> NoReturn:
        categories = ['rec.autos', 'comp.graphics', 'sci.med']
        to_remove = ['footers', 'quotes']
        subset = 'train'  # 'test' or 'train'

        # get data
        raw_data = fetch_20newsgroups(subset=subset, categories=categories, remove=to_remove)
        df_data = self.get_dataframe_from_dict_like_data(raw_data, keys=['data', 'target'])

        # add subject column
        subjects = Series([self.get_subject(text) for text in df_data['data']])
        df_data['subject'] = subjects

        # add target_name column
        target_names = Series([raw_data['target_names'][target] for target in df_data['target']])
        df_data['target_name'] = target_names

        # add text column
        processed_texts = Series([self.get_processed_text(text) for text in df_data['data']])
        df_data['text'] = processed_texts

        # remove rows with empty text
        nan_value = float("NaN")
        df_data.replace('', nan_value, inplace=True)
        df_data.dropna(subset=['text'], inplace=True)
        df_data = df_data.reset_index()

        self._create_plone_content(df_data, document_type)

        return True
