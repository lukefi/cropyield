# vanhalla Macilla
# ajetaan kaikki vuodet, koska nyt y mukana ID:ssä, helpompi ja varmempi näin. Voidaan käyttää 08-makeTarget.sh
# jotain häikkää oli myös aiemmissa datoissa, kun osassa id oli farmID ja osassa parcelID.

# 1. vuosi 2023 kaikki (paitsi ruokaherne):

python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2023/Kasvulohkot2023.gpkg \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-y 2023 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2023/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5

# puuttuva 2100 ruokaherne:
python 00-preprecessing-training-set-with-Pinja-data.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2023/Kasvulohkot2023.gpkg \
-j /Users/myliheik/Documents/myCROPYIELD/data/viljelijakysely/Pinjalta_select_sv_vuosi_sv_tilatunnus_sv_kasitekoodi1_sk_kod_selite_fi1_2023.csv \
-y 2023 \
-o /Users/myliheik/Documents/myCROPYIELD/data/training-2023/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 2100

## data kunnossa vuonna 2023 (korjauksin tosin, koodissa)

# 3. yhdistä yo.:t notebooksissa (pd.concat)

# 4. vuosi 2022 vanhoista:
python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2022/kasvulohkot2022-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/Satotiedot_2022_Marialle.csv-mod \
-y 2022 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2022/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 1110 1120 1230 1310 1320 1400 2100 2200 3100

## Puuttuvat:
python ../python/00-preprecessing-training-set-with-Pinja-data.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2022/kasvulohkot2022-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/Pinjalta-vuosi2022-noDuplicates.csv \
-y 2022 -o /Users/myliheik/Documents/GISdata/satotutkimus/training-2022/ -s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 4100

# Mirvan uudesta data rapsi:
python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2022/kasvulohkot2022-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-y 2022 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2022/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 4200


# 5. yhdistä 2022 notebooksissa (pd.concat)

# 6. vuosi 2021
python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2021/kasvulohkot2021-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-y 2021 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2021/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5

# 7. vuosi 2020
python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2020/kasvulohkot2020-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-y 2020 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2020/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5

# 8. vuosi 2019
python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2019/kasvulohkot2019-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-y 2019 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2019/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5

# 9. vuosi 2018
python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2018/kasvulohkot2018-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-y 2018 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2018/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5

