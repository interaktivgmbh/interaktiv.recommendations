# interaktiv.recommendations

![Python Version](https://img.shields.io/badge/Python-~=3.8-blue "Plone Version")

Interaktiv Recommendations plone package.

## Table of contents

1. [Installation](#installation)
   1. [Add the recommendation package to the backend](#1-add-the-recommendations-package-to-the-backend)
   2. [Add the volto recommendation package to the frontend (Volto only)](#2-add-the-volto-recommendations-package-to-the-frontend-volto-only)
   3. [Start "buildout" and for Volto additionally "yarn install"](#3-start-buildout-and-for-volto-additionally-yarn-install)
2. [How to enable the recommendations](#how-to-enable-the-recommendations)
   1. [Enable recommendations behavior](#1-enable-recommendations-behavior)
   2. [Update recommendations index](#2-update-recommendations-index)
3. [Copyright and License](#copyright-and-license)


## Installation
### 1. Add the recommendations package to the backend
#### File: buildout.cfg
```
[sources]
...
interaktiv.recommendations = git git@github.com:interaktivgmbh/interaktiv.recommendations.git branch=main
```
```
eggs =
    ...
    interaktiv.recommendations
```


### 2. Add the volto recommendations package to the frontend (Volto only)
#### File: mrs.developer.json
```json
{
  "volto-recommendations": {
    "url": "git@github.com:interaktivgmbh/volto-recommendations.git",
    "path": "src",
    "package": "@interaktiv/volto-recommendations",
    "branch": "main"
  }
}
```
#### File: package.json
```json
  "addons": [
    "@interaktiv/volto-recommendations"
  ]
```

### 3. Start "buildout" and for Volto additionally "yarn install"

## Enable the recommendations
### 1. Enable recommendations behavior
Enable the recommendations behavior on a contenttype of your choice via controlpanel **/@@dexterity-types**.

### 2. Update recommendations index
#### Plone classic:
Open **/@@recommendations_settings** and click on the **Refresh-Button**.

#### Volto:
Open **/controlpanel/recommendations** and click on the **Refresh-Button**.

# Copyright and License
Author: Interaktiv GmbH - https://interaktiv.de

Copyright (c) 2022, Interaktiv GmbH

See LICENSE.md for details.