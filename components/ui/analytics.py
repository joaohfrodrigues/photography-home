"""Vercel Web Analytics component for FastHTML

This module provides Vercel Web Analytics integration for server-rendered FastHTML applications.
It includes the necessary scripts to track page views and web metrics.

Reference: https://vercel.com/docs/analytics/getting-started
"""

from fasthtml.common import *


def create_analytics():
    """Create Vercel Web Analytics scripts for server-rendered HTML applications.

    This function returns the necessary scripts to enable Vercel Web Analytics tracking
    on your FastHTML application. The scripts are non-intrusive and support route tracking
    automatically for single-page applications.

    Returns:
        A tuple of Script elements to be included in the HTML body.

    Note:
        - These scripts should be placed in the HTML body, preferably near the end
        - The analytics tracking happens automatically on page load
        - No manual route tracking is needed for standard page navigation
    """
    return (
        # Initialize the Vercel Analytics API
        Script(
            NotStr("""
    window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
            """),
            # Safely inline the initialization
        ),
        # Load the Vercel Web Analytics tracking script
        # Use hosted Vercel analytics script so it works in local dev too
        Script(
            src='https://va.vercel-scripts.com/v1/script.js',
            defer=True,
            # The script is deferred to not block page rendering
        ),
    )
