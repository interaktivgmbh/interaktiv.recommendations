# interaktiv.recommendations

![Python Version](https://img.shields.io/badge/Python-~=3.8-blue "Plone Version")

Interaktiv Recommendations plone package.

## Installation
### 1. Add recommendations to the backend
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


### 2. Add recommendations to the frontend (Volto only)
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
    ...
    "@interaktiv/volto-recommendations"
  ]
```

### 3. Start "buildout" and for Volto additionally "yarn install"

## How to enable the recommendations

### 1. Add recommendationsecommendations behavior
#### Add recommendations behavior (as seen below) to a contenttype of your choice via management-interface > portal_types.
```
interaktiv.recommendations.behaviors.recommendable.IRecommendableBehavior
```


### 2. Update recommendations index
#### Plone classic:
Open **/@@recommendations_settings** and click on the **Refresh-Button**.

#### Volto:
Open **/controlpanel/recommendations** and click on the **Refresh-Button**.

# Copyright and License
Author: Interaktiv GmbH - https://interaktiv.de

Copyright (c) 2022 Plone Foundation

See LICENSE.md for details.