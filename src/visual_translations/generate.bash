#!/bin/bash

cd ..
python manage.py generate_eu_visual_translations -a immigrants --delete
python manage.py generate_eu_visual_translations -a privatization
python manage.py generate_eu_visual_translations -a peace
python manage.py generate_eu_visual_translations -a cowshed
python manage.py generate_eu_visual_translations -a pension
python manage.py generate_eu_visual_translations -a women
python manage.py generate_eu_visual_translations -a nature
python manage.py generate_eu_visual_translations -a credit
python manage.py generate_eu_visual_translations -a leave
python manage.py generate_eu_visual_translations -a law
python manage.py generate_eu_visual_translations -a justice
python manage.py generate_eu_visual_translations -a virus
python manage.py generate_eu_visual_translations -a vaccine
python manage.py generate_eu_visual_translations -a corona
python manage.py generate_eu_visual_translations -a brexit
cd -
