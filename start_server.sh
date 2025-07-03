#!/bin/bash
cd "/Users/tflan1213/git/thrashy/mcp-newrelic"
exec "/Users/tflan1213/.pyenv/versions/3.11.8/bin/uv" run python server.py "$@"