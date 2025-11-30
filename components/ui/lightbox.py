"""Lightbox modal component"""

from fasthtml.common import *


def create_lightbox():
    """Create the lightbox modal for viewing photos"""
    return Div(
        Div(
            Button('×', cls='lightbox-close', onclick='closeLightbox()'),
            Button('‹', cls='lightbox-nav lightbox-prev', onclick='navigateLightbox(-1)'),
            Button('›', cls='lightbox-nav lightbox-next', onclick='navigateLightbox(1)'),
            Div(
                Div(
                    Img(src='', alt='', id='lightbox-img', cls='lightbox-image'),
                    cls='lightbox-image-container',
                ),
                Div(
                    H2('', id='lightbox-title', cls='lightbox-title'),
                    P(
                        '',
                        id='lightbox-index',
                        cls='lightbox-index',
                        style='font-size: 0.9rem; color: #888; margin: 0.5rem 0;',
                    ),
                    P('', id='lightbox-description', cls='lightbox-description'),
                    # Basic Info
                    Div(
                        Div(cls='lightbox-section-title', innerText='Details'),
                        Div(
                            Span('Date', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-created'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                        ),
                        Div(
                            Span('Size', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-dimensions'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                        ),
                        Div(
                            Span('Location', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-location'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            style='display: none;',
                        ),
                        cls='lightbox-meta',
                    ),
                    # Camera Info
                    Div(
                        Div(cls='lightbox-section-title', innerText='Camera Settings'),
                        Div(
                            Span('Camera', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-camera'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='camera-item',
                        ),
                        Div(
                            Span('Shutter', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-exposure'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='exposure-item',
                        ),
                        Div(
                            Span('Aperture', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-aperture'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='aperture-item',
                        ),
                        Div(
                            Span('Focal Length', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-focal'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='focal-item',
                        ),
                        Div(
                            Span('ISO', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-iso'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='iso-item',
                        ),
                        cls='lightbox-meta',
                        id='camera-section',
                    ),
                    # Tags
                    Div(
                        Div(cls='lightbox-section-title', innerText='Tags'),
                        Div(id='meta-tags', cls='lightbox-tags'),
                        cls='lightbox-tags-section',
                    ),
                    # Stats
                    Div(
                        Div(cls='lightbox-section-title', innerText='Stats'),
                        Div(
                            Span('Views', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-views'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='stats-views',
                        ),
                        Div(
                            Span('Downloads', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-downloads'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='stats-downloads',
                        ),
                        cls='lightbox-meta',
                        id='stats-section',
                    ),
                    # Attribution
                    Div(
                        Div(cls='lightbox-section-title', innerText='Attribution'),
                        Div(
                            P(
                                Span('Photo by '),
                                A(
                                    'Photographer',
                                    id='photographer-link',
                                    href='#',
                                    target='_blank',
                                    rel='noopener noreferrer',
                                    style='color: #aaa; text-decoration: underline;',
                                ),
                                Span(' on '),
                                A(
                                    'Unsplash',
                                    href='https://unsplash.com',
                                    target='_blank',
                                    rel='noopener noreferrer',
                                    style='color: #aaa; text-decoration: underline;',
                                ),
                                style='font-size: 0.85rem; color: #666; margin: 0;',
                            ),
                            Div(
                                A(
                                    'View on Unsplash →',
                                    id='unsplash-link',
                                    href='#',
                                    target='_blank',
                                    rel='noopener noreferrer',
                                    style='color: #888; text-decoration: none; font-size: 0.85rem; display: inline-block; margin-top: 0.5rem;',
                                ),
                            ),
                            cls='lightbox-meta-item',
                            style='display: block;',
                        ),
                        cls='lightbox-meta',
                    ),
                    cls='lightbox-details',
                ),
                cls='lightbox-content',
            ),
            cls='lightbox',
            id='lightbox',
            onclick='event.target.id === "lightbox" && closeLightbox()',
        )
    )
