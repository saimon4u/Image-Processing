# Image sources

Clean images only. Degraded copies are synthesized by `degradations.py`.

## Medical — frontal chest X-ray

- `cxr_github_01.png` — ieee8023/covid-chestxray-dataset, frontal CXR (Cohen et al.)
- `cxr_github_02.png` — ieee8023/covid-chestxray-dataset, PA CXR (`nejmoa2001191_f1-PA`)
- `cxr_github_03.png` — ieee8023/covid-chestxray-dataset, frontal CXR (`lancet-case2a`)
- `cxr_github_04.png` — ieee8023/covid-chestxray-dataset, frontal CXR (`ryct.2020200028.fig1a`)
- `cxr_github_05.png` — ieee8023/covid-chestxray-dataset, PA CXR (`covid-19-pneumonia-7-PA`)
- `cxr_github_06.png` — ieee8023/covid-chestxray-dataset, PA CXR (`nejmoa2001191_f3-PA`)

## Satellite / remote sensing — optical RGB (UC Merced / USGS National Map)

- `ucmerced_agricultural.png` — UC Merced Land Use, agricultural00 (Yang & Newsam 2010)
- `ucmerced_beach.png` — UC Merced Land Use, beach00
- `ucmerced_buildings.png` — UC Merced Land Use, buildings00
- `ucmerced_forest.png` — UC Merced Land Use, forest00
- `ucmerced_harbor.png` — UC Merced Land Use, harbor00
- `ucmerced_river.png` — UC Merced Land Use, river00

## Attribution notes

- Chest X-rays: Cohen, J.P. et al., *covid-chestxray-dataset*. Only frontal PA/AP radiographs are used (one medical image type).
- UC Merced Land Use: Yang, Y. & Newsam, S. (2010), *Bag-of-visual-words and spatial extensions for land-use classification*, ACM SIGSPATIAL. Scenes are 0.3 m optical RGB extracted from the USGS National Map Urban Area Imagery collection.
- Degradations (salt-and-pepper, additive Gaussian noise, Gaussian blur) are synthesized in this experiment so that every degraded image has a paired clean reference.
