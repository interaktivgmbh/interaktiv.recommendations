import os
import sys
import transaction
import plone.api as api
from typing import NoReturn


class ScriptWrapper:
    """
    Instance script for updating recommendations
    Example usage:
    bin/instance -Osite run src/interaktiv.recommendations/src/interaktiv/
    recommendations/scripts/refresh_recommender.py
    """

    @staticmethod
    def run() -> NoReturn:
        recommender = api.portal.get_tool('portal_recommender')
        recommender.refresh()
        transaction.commit()
        return


if __name__ == "__main__":
    if 'obj' not in globals():
        print("No Plone Site defined. Exiting..")
        sys.exit()

    script_wrapper = ScriptWrapper()
    script_wrapper.run()
    os._exit(0)
