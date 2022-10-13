# https://matplotlib.org/stable/gallery/text_labels_and_annotations/angle_annotation.html

import pandas as pd
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.transforms import IdentityTransform, TransformedBbox, Bbox


class AngleAnnotation(Arc):
    """
    Draws an arc between two vectors which appears circular in display space.
    """
    def __init__(self, xy, p1, p2, size=75, unit="points", ax=None,
                 text="", textposition="inside", text_kw=None, **kwargs):
        """
        Parameters
        ----------
        xy, p1, p2 : tuple or array of two floats
            Center position and two points. Angle annotation is drawn between
            the two vectors connecting *p1* and *p2* with *xy*, respectively.
            Units are data coordinates.

        size : float
            Diameter of the angle annotation in units specified by *unit*.

        unit : str
            One of the following strings to specify the unit of *size*:

            * "pixels": pixels
            * "points": points, use points instead of pixels to not have a
              dependence on the DPI
            * "axes width", "axes height": relative units of Axes width, height
            * "axes min", "axes max": minimum or maximum of relative Axes
              width, height

        ax : `matplotlib.axes.Axes`
            The Axes to add the angle annotation to.

        text : str
            The text to mark the angle with.

        textposition : {"inside", "outside", "edge"}
            Whether to show the text in- or outside the arc. "edge" can be used
            for custom positions anchored at the arc's edge.

        text_kw : dict
            Dictionary of arguments passed to the Annotation.

        **kwargs
            Further parameters are passed to `matplotlib.patches.Arc`. Use this
            to specify, color, linewidth etc. of the arc.

        """
        self.ax = ax or plt.gca()
        self._xydata = xy  # in data coordinates
        self.vec1 = p1
        self.vec2 = p2
        self.size = size
        self.unit = unit
        self.textposition = textposition

        super().__init__(self._xydata, size, size, angle=0.0,
                         theta1=self.theta1, theta2=self.theta2, **kwargs)

        self.set_transform(IdentityTransform())
        self.ax.add_patch(self)

        self.kw = dict(ha="center", va="center",
                       xycoords=IdentityTransform(),
                       xytext=(0, 0), textcoords="offset points",
                       annotation_clip=True)
        self.kw.update(text_kw or {})
        self.text = ax.annotate(text, xy=self._center, **self.kw)

    def get_size(self):
        factor = 1.
        if self.unit == "points":
            factor = self.ax.figure.dpi / 72.
        elif self.unit[:4] == "axes":
            b = TransformedBbox(Bbox.unit(), self.ax.transAxes)
            dic = {"max": max(b.width, b.height),
                   "min": min(b.width, b.height),
                   "width": b.width, "height": b.height}
            factor = dic[self.unit[5:]]
        return self.size * factor

    def set_size(self, size):
        self.size = size

    def get_center_in_pixels(self):
        """return center in pixels"""
        return self.ax.transData.transform(self._xydata)

    def set_center(self, xy):
        """set center in data coordinates"""
        self._xydata = xy

    def get_theta(self, vec):
        vec_in_pixels = self.ax.transData.transform(vec) - self._center
        return np.rad2deg(np.arctan2(vec_in_pixels[1], vec_in_pixels[0]))

    def get_theta1(self):
        return self.get_theta(self.vec1)

    def get_theta2(self):
        return self.get_theta(self.vec2)

    def set_theta(self, angle):
        pass

    # Redefine attributes of the Arc to always give values in pixel space
    _center = property(get_center_in_pixels, set_center)
    theta1 = property(get_theta1, set_theta)
    theta2 = property(get_theta2, set_theta)
    width = property(get_size, set_size)
    height = property(get_size, set_size)

    # The following two methods are needed to update the text position.
    def draw(self, renderer):
        self.update_text()
        super().draw(renderer)

    def update_text(self):
        c = self._center
        s = self.get_size()
        angle_span = (self.theta2 - self.theta1) % 360
        angle = np.deg2rad(self.theta1 + angle_span / 2)
        r = s / 2
        if self.textposition == "inside":
            r = s / np.interp(angle_span, [60, 90, 135, 180],
                                          [3.3, 3.5, 3.8, 4])
        self.text.xy = c + r * np.array([np.cos(angle), np.sin(angle)])
        if self.textposition == "outside":
            def R90(a, r, w, h):
                if a < np.arctan(h/2/(r+w/2)):
                    return np.sqrt((r+w/2)**2 + (np.tan(a)*(r+w/2))**2)
                else:
                    c = np.sqrt((w/2)**2+(h/2)**2)
                    T = np.arcsin(c * np.cos(np.pi/2 - a + np.arcsin(h/2/c))/r)
                    xy = r * np.array([np.cos(a + T), np.sin(a + T)])
                    xy += np.array([w/2, h/2])
                    return np.sqrt(np.sum(xy**2))

            def R(a, r, w, h):
                aa = (a % (np.pi/4))*((a % (np.pi/2)) <= np.pi/4) + \
                     (np.pi/4 - (a % (np.pi/4)))*((a % (np.pi/2)) >= np.pi/4)
                return R90(aa, r, *[w, h][::int(np.sign(np.cos(2*a)))])

            bbox = self.text.get_window_extent()
            X = R(angle, r, bbox.width, bbox.height)
            trans = self.ax.figure.dpi_scale_trans.inverted()
            offs = trans.transform(((X-s/2), 0))[0] * 72
            self.text.set_position([offs*np.cos(angle), offs*np.sin(angle)])


def plot_vectorizer_result(vectorizer, texts, word_a='house', word_b='green', tickspacing=0.5):
    text_labels = ['text_a', 'text_b', 'unknown_text']
    text_colors = ['g', 'b', 'r']

    # get data from vectorizer
    vectors = vectorizer.transform(texts).toarray()
    words = list(vectorizer.get_feature_names_out())
    word_a_index = vectorizer.vocabulary_[word_a]
    word_b_index = vectorizer.vocabulary_[word_b]

    # create dataframe
    data = {
        'text': [text_labels[i] for i in range(len(texts))]
    }
    for index, word in enumerate(words):
        data[word] = ["{:10.2f}".format(vector[index]) for vector in vectors]

    vectors_dataframe = pd.DataFrame(data=data)
    vectors_dataframe.set_index('text')

    # create vectors
    origins_x = [0 for vector in vectors]
    origins_y = [0 for vector in vectors]
    values_x = [vector[word_a_index] for vector in vectors]
    values_y = [vector[word_b_index] for vector in vectors]
    max_value = max(max(values_x), max(values_y))

    # create figure
    # fig = plt.figure(figsize=(14, 4))
    fig, ax = plt.subplots(1, 2, figsize=(18, 4), gridspec_kw={'width_ratios': [3, 5]})
    # fig.tight_layout()

    # plot vectors
    # ax[0] = fig.add_subplot(1, 2, 1)
    ax[0].set_title(f'Vectors for Words "{word_a}" and "{word_b}"')
    ax[0].grid(True)
    ax[0].xaxis.set_major_locator(ticker.MultipleLocator(tickspacing))
    ax[0].yaxis.set_major_locator(ticker.MultipleLocator(tickspacing))
    #
    ax[0].set_xlim([0, max_value + max_value * 0.25 * 0.5])
    ax[0].set_xlabel(word_a)
    ax[0].set_ylim([0, max_value + max_value * 0.25 * 0.5])
    ax[0].set_ylabel(word_b)
    #
    ax[0].quiver(
        origins_x, origins_y,
        values_x, values_y,
        angles='xy', scale_units='xy', scale=1, color=text_colors
    )
    #
    for index in range(len(vectors)):
        ax[0].text(values_x[index], values_y[index], text_labels[index], color=text_colors[index])

    #
    if len(vectors) > 2:
        am2 = AngleAnnotation(
            [0, 0],
            [values_x[2], values_y[2]],
            [values_x[1], values_y[1]],
            ax=ax[0], size=300, text=r"$\beta$"
        )

        am1 = AngleAnnotation(
            [0, 0],
            [values_x[0], values_y[0]],
            [values_x[2], values_y[2]],
            ax=ax[0], size=400, text=r"$\alpha$"
        )

    # plot data table
    # ax_d = fig.add_subplot(1, 2, 2)
    ax[1].axis('off')
    ax[1].axis('tight')
    table = ax[1].table(cellText=vectors_dataframe.values, colLabels=vectors_dataframe.columns, loc='center')
    # table.set_fontsize(6)
    # table.scale(1.2, 1.2)
