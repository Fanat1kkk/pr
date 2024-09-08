#!/bin/bash
source /home/sasha/toppr_site/env/bin/activate
exec gunicorn -c /home/sasha/toppr_site/top_pr/gunicorn_config.py top_pr.wsgi
