SportsNet
=========

[![Coverage Status](https://coveralls.io/repos/github/iarp/SportsNet/badge.svg?branch=master)](https://coveralls.io/github/iarp/SportsNet?branch=master)
[![Django CI](https://github.com/iarp/SportsNet/actions/workflows/django.yml/badge.svg)](https://github.com/iarp/SportsNet/actions)


The primary repository for the SK to SportsNet conversion.

Current goals:

- Merge SK Desktop into SportsNet:
  - Move tables from SK tables into django models
  - Remove all use of MSSQL in favor of django models
  - Setup new views and templates for what the desktop version did
- Merge SK Web into SportsNet:
  - Copy existing tables into new project
  - Relink all tables to newly merged SKDesktop tables in django models

Future Goals:

- Merge tryout portal into SportsNet Web
- Setup drafting system
