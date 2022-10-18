
import numpy as np
import os
from shapely.geometry import Point, Polygon
import geopandas as gpd
import json
import pyproj
from shapely.geometry import MultiPolygon, Polygon, MultiLineString, LineString
from shapely.ops import transform as sh_transform
from functools import partial
import fiona
from copy import deepcopy
from shapely import wkt
import requests
import geojson
import time
import sys
from ipywidgets import Button
import shapely
#from tkinter import Tk, filedialog
import math
#from tkinter import Tk, filedialog
#import tkinter
#For Map Display
from IPython.display import clear_output, display
import contextily as cx
import folium
import fiona
import pandas as pd
import alphashape

### The below section is for the core non iterative functions that are used in more complex functions later.


#This is the start of removing donuts IT has not been tested.
def remove_donuts(gdf):
    exterior = []
    for row in gdf.itertuples():
        polygon=getattr(row,'geometry')
        gdf_index=getattr(row,'Index')
        gdf.at[gdf_index,'geometry'] = Polygon(polygon.exterior.coords)
        if polygon != Polygon(polygon.exterior.coords):
            if 'donuts_removed' in gdf.columns:
                gdf.at[gdf_index,'donuts_removed']="True"
            
            else:
                gdf.insert(loc=1,column="donuts_removed",value="True")
        else:
            if 'donuts_removed' in gdf.columns:
                gdf.at[gdf_index,'donuts_removed']="False"
            
            else:
                gdf.insert(loc=1,column="donuts_removed",value="False")

    return gdf



def remove_donuts_old(gdf):
    exterior = []
    for row in gpd.itertuple(gdf):
    #for cur_row in range(len(gdf)):
        #print row
        cur_row_gdf=gdf.iloc[[cur_row]]
        polygon=gdf['geometry'][cur_row]
        polygon2=polygon.exterior.coords
        #polygs=gpd.GeoSeries(polygon2)
        #polygon3=Polygon(simplegs.iloc[0].exterior.coords)
            #print(simple)
            #gdf=gpd.GeoDataFrame(gdf)
            #len(gdf2)
        gdf.loc[[cur_row], 'geometry']= polygon2
        #polygon3=Polygon(polygon2)
        #exterior.append(polygon3)

    #newgs=gpd.GeoSeries(exterior)
    #gdf2 = gpd.GeoDataFrame(deepcopy(gdf), geometry=newgs)    

    #return gdf2

def simply_poly(gdf):
    for cur_row in range(len(gdf)):
        #print(len(gdf))
        print(f'cur row is {cur_row}')
        cur_row_gdf=gdf.iloc[[cur_row]]
        geom=cur_row_gdf.geometry
        points=geom.iloc[0].exterior.coords
        print(len(points))
        #print(points)
        #print(len(points))
        simplify_amount=0.000005
        count=0
        
        if len(points)<500:
            simplify_return=('geometery did not need to be simplified') 
        
        else:
            while len(points) >=500 and count < 51:



                #print(f'shape area is {cur_row_gdf['area'][0]}')
                print(f'toobig! there are {len(points)} vertices')
                gs=cur_row_gdf.geometry
                #print(type(gs))
                simplegs=gs.simplify(simplify_amount)
                print(len(simplegs.iloc[0].exterior.coords))
                simplegdf=gpd.GeoDataFrame(geometry=simplegs)

                simple=Polygon(simplegs.iloc[0].exterior.coords)
                #print(simple)
                #gdf=gpd.GeoDataFrame(gdf)
                #len(gdf2)
                gdf.loc[[cur_row], 'geometry']= simple
                cur_row_gdf.loc[[cur_row],'geometry']=simple
                geom=cur_row_gdf.geometry
                points=geom.iloc[0].exterior.coords
                #simplify_return = (f'vertices reduced to {len(points)} with a simplified amount of {simplify_amount} degrees after {count} iterations. 1 degree is roughtly 111km. 0.0001 degree is 11.1m roughly')
                simplify_amount=simplify_amount+0.000005
                #print(simplify_amount)
                count=count+1
                
                # This could be increased to 0.0001 as it used to be.
                if simplify_amount > 0.00002 or count==50:
                    simplify_return=('geometery could not be simplified')
                    pass                
                    
                #     envelopegs=deepcopy(cur_row_gdf).geometry.convex_hull
                #     envelope=Polygon(envelopegs.iloc[0].exterior.coords)
                #     gdf.loc[[cur_row], 'geometry'] = envelope

                #     print('geometry could not be simplified, so convex hull was created')

                #else:
                    #simplify_return='geometry could not be simplified'
                if len(points) < 500:
                    simplify_return=(f'vertices reduced to {len(points)} with a simplified amount of {simplify_amount} degrees after {count} iterations. 1 degree is roughtly 111km. 0.0001 degree is 11.1m roughly')
            
            

        if not simplify_return:
            simplify_return='it did not need to be simplified'
        
        if 'simplified' in gdf.columns:
            gdf.loc[[cur_row],'simplified']=simplify_return            
        else:
            gdf.insert(loc=1,column="simplified",value=simplify_return)

    return gdf

        #simplify_list=[str(simplify_amount),simplify_return]


        #return simplify_list


    # for cur_row in range(len(gdf)):
    #     print(len(gdf))
    #     print(cur_row)
    #     cur_row_gdf=gdf.iloc[[cur_row]]
    #     geom=cur_row_gdf.geometry
    #     points=geom.iloc[0].exterior.coords
    #     print(len(points))
    #     #print(points)
    #     #print(len(points))
    #     simplify_amount=0.00005
    #     count=0
    #     while len(points) >=500:

    #         #print(f'shape area is {cur_row_gdf['area'][0]}')
    #         print(f'toobig! there are {len(points)} vertices')
    #         simplegs=cur_row_gdf.geometry.simplify(simplify_amount)
    #         simple=Polygon(simplegs.iloc[0].exterior.coords)
        
            
    #         gdf.loc[[cur_row], 'geometry']= simple
    #         cur_row_gdf.loc[[cur_row],'geometry']=simple
    #         geom=cur_row_gdf.geometry
    #         points=geom.iloc[0].exterior.coords
    #         print(f'vertices reduced to {len(points)} with a simplified amount of {simplify_amount} degrees after {count} iterations. 1 degree is roughtly 111km. 0.0001 degree is 11.1m roughly')
    #         simplify_amount=simplify_amount+0.00005
    #         count=count+1

    #     #else:
    #         #print('shape did not need to be simplified')
            
    #         if simplify_amount > 0.0001:
    #             envelopegs=deepcopy(cur_row_gdf).geometry.convex_hull
    #             envelope=Polygon(envelopegs.iloc[0].exterior.coords)
    #             gdf.loc[[cur_row], 'geometry'] = envelope

    #             print('geometry could not be simplified, so convex hull was created')
    #             break
    #         elif count > 50:
    #             ('geometry could not be simplified')
    #         else:
    #             "cannot simplify"
    #             break
            





    return gdf


#This iterates through geometry and if z data exists removes it from Polygons and MultiPolygons. It also explodes MultiPolygons into Polygons
def clean_data(gdf):
    #Takes a GeoSeries of 3D Multi/Polygons (has_z) and returns a list of 2D Multi/Polygons
    
    for row in gdf.itertuples():

        if getattr(row,'geometry')== None:
            gdf=gdf.drop(getattr(row,'Index'))
            print(True)

    gdf=gdf.explode()
    gdf=gdf.reset_index(drop=True)
    count=1



    for cur_row in range(len(gdf)):
        cur_row_gdf=gdf.iloc[[cur_row]]
        geometry = cur_row_gdf['geometry']
        new_geo=[]


        #print(geometry)
        #geometry=gdf.loc[gdf.geometry]
        for p in geometry:
            print(p.geom_type)
            print(f'polygon number {count}')
            count=count+1
            if p.has_z==True:
                print('geometry has z? = {}'.format(p.has_z))
                if p.geom_type == 'Polygon':
                    print('geometry of type polygon exists?{}'.format(p.geom_type=='Polygon'))
                    lines = [xy[:2] for xy in list(p.exterior.coords)]
                    new_p = Polygon(lines)
                    gdf.loc[[cur_row], 'geometry'] = new_p
    #             print(new_geo)
    #             newgs=gdf.GeoSeries(new_geo)
    #             new_geo=gdf.GeoDataFrame(gdf, geometry=new_geo)
                # elif p.geom_type == 'MultiPolygon':
                #     print('geometry of type multipolygon exists?{}'.format(p.geom_type=='MultiPolygon'))
                #     new_multi_p = []
                #     for ap in p:
                #         lines = [xy[:2] for xy in list(ap.exterior.coords)]
                #         new_p = Polygon(lines)
                #         new_multi_p.append(new_p)
                #         multipoly=MultiPolygon(new_multi_p)
                #         gdf.loc[[cur_row],'geometry']=gpd.GeoSeries(multipoly)

                # elif p.geom_type == 'MultiLineString':
                #     print('geometry of type multipolygon exists?{}'.format(p.geom_type=='MultiLineString'))
                #     new_multi_l = []
                #     for al in p:
                #         lines = [xy[:2] for xy in list(al.coords)]  
                #         new_l = LineString(lines)
                #         new_multi_l.append(new_l)
                #         multiline=MultiLineString(new_multi_l)
                #         gs=gpd.GeoSeries(multiline)
                #         gdf.loc[[0],'geometry']=gs

            #print(new_geo)
            elif p.has_z == False:
                print('no z values detected')
    #print('explosion time')            
    #explode=gdf.explode()

    #gdf2=explode.reset_index(drop=True)
                
    return gdf

#This function takes an input kml and turns it into a geodataframe.
def load_kml(infile):

    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    #gdf=gpd.GeoDataFrame()
    count=0
    #for layer in fiona.listlayers(infile): 
        
    if len(fiona.listlayers(infile)) >= 2:

        print('kml has too many layers')
        pass
    
    else:

        #gdf = gpd.read_file(infile, driver='KML')
        gdf= gpd.read_file(infile, driver='KML') #layer=layer add to get layers in a fiona.lilstlayers for loop
        #gdf = gpd.concat([gdf, s], ignore_index=True)
        return gdf

    
    


   # return gdf

#Check Projection
def projection_check(gdf):
    if gdf.crs =='epsg:4326':
        proj='projection is in 4326'
        goodproject=True
    elif gdf.crs != 'epsg:4326':
        proj='please project your data to 4326'
        goodproject=False
    return goodproject

#Function to load geojson, json, kml, kmz, csv (with Lat and Long columns), shapefile
#Requirements - best if in wgs1984 although building out functionality to convert on the fly.

def load_file(infile):
    
    extension=infile.rsplit('.',1)[-1]
    
    if extension in ['geojson','json','shp']:
        gdf=gpd.read_file(infile)
        gdf=gpd.GeoDataFrame(gdf)
        return gdf
        #print('file type is {}'.format(extension[-1]))
        #gdf
        #return gdf
    elif extension=='kml':
        gdf=load_kml(infile)
        return gdf

    elif extension=='csv':
        gdf = gpd.read_file(infile)
        gdf = gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(gdf['Long'], gdf['Lat']))
        gdf.set_crs(4326)
        return gdf

    #elif extension[-1]=='':
        #files = os.listdir(infile)

        #for f in files:
            #load_file(f)
            
    else:
        print('File type not recognized. Please provide geojson, csv or kml')


    


# This function will create a projection for a single polygon. Can be used in an iterator

#Function to Buffer geodesic data in a local equal area projection. This lets you put in a value in meters for the buffer. 
#It creates a centroid for each individual feature and makes a local coordinate system - this means it works over large areas as it
#iteratively creates EAP for each polygon or point. 
#It then takes the geometry for the EAP in that loop and buffers it, then transforms it back to wgs84. The geometry gets 
def EAProject_Buffer(gdf,radius,capstyle=1):
    bufflist=[]

    #Takes a geodataframe
    for cur_row in range(len(gdf)):
    #makes subset geodataframe at cur row
        pol2=gdf.iloc[[cur_row]]

        #gets geometry of the dataframe at the current row.
        geom=pol2.geometry[cur_row]
        #for projection
        wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')

        if geom.geom_type in ['Polygon','MultiPolygon','MultiLineString','LineString']:
            _lon, _lat = geom.centroid.coords[0]
            #cent=gdfpol.centroid #Note this logic hasn't been tested yet.
            #print('poly')
        elif geom.geom_type in ['Point']:
            #print('point')
            _lon, _lat = geom.centroid.coords[0]
            #print(pol.coords)


        aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=_lat, lon_0=_lon)

        projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), geom)
        #print(projpol)
        buffpol=projpol.buffer(radius,cap_style=capstyle)
        temp2=gpd.GeoDataFrame(pol2,geometry=[buffpol])
        output=sh_transform(partial(pyproj.transform, aeqd, wgs84_globe),buffpol)
        # bufflist.append(output)
        gdf.loc[[cur_row], 'geometry'] = output

    return gdf    


    # buffgs=gpd.GeoSeries(bufflist)
    # output=gpd.GeoDataFrame(deepcopy(gdf),geometry=buffgs)
    # outgdf=output.set_crs(4326)
    # return outgdf

def optimize_area(gdfclean,quote_type,resolution,minarea,data_type='Corridors'):
    ### Need to find a way to check min area in the file and only start buffer interval there. I.e if min area is 0.65, start buffer_interval at 0.8.
    if quote_type == "Tasking":
        radius=200  #radius to buffer in iteration (in m)
        if minarea <25000000:
            minarea=25
            radius=200  #radius to buffer in iteration (in m)
            buffer_interval=1
        else:
            minarea=minarea/1000000
            if minarea%5==0:
                buffer_interval=5
            elif minarea%3==0:
                buffer_interval=3
            elif minarea%2==0:
                buffer_interval=2
            elif minarea%1==0:
                buffer_interval=1
            else:
                print('area must be a whole number')
                exit()
        #minarea=25# minimum area to hit (in km2)
        
        
    elif quote_type == "Archive" and (resolution=="high" or resolution == "very_high"):
        radius=50
        #minarea=1
        if minarea <=1000000:
            minarea=1
            radius=50  #radius to buffer in iteration (in m)
            buffer_interval=0.2
        else:
            minarea=minarea/1000000
            buffer_interval=minarea/5
    
    elif quote_type == "Archive" and resolution=="medium":
        if minarea <1000:
            minarea=0.1
            radius=50  #radius to buffer in iteration (in m)
            buffer_interval=0.05
        else:
            minarea=minarea/1000000
            buffer_interval=minarea/5

    else: 
        print('quote type does not match options.')
        exit()

    print(buffer_interval)        
    gdfbuff=gpd.GeoDataFrame(deepcopy(gdfclean))


    while buffer_interval <= minarea: # while 0.4 <= 1
        print(f'minimum area value is {min(gdfbuff["optimized_area"].values)}')
        #while (min(gdfbuff['area'].values))<= buffer_interval: # if min gdf area < 1
        #while buffer_interval < minarea:
        print(f'interval buffer is {buffer_interval}')
        print(f'minimum area is {min(gdfbuff["optimized_area"].values)}')

        gdfbuff=EAProject_BuffersSubset(deepcopy(gdfbuff),radius,buffer_interval,minarea)
        gdfbuff=gdfbuff.dissolve()
        gdfbuff=gdfbuff.explode()
        gdfbuff=gdfbuff.reset_index(drop=True)
        
        if data_type != 'Corridors':

            gdfbuff=remove_donuts(deepcopy(gdfbuff))

        else:
            pass
        
        #gdfbuff=sw.aoi_areakm(gdfbuff,'tasking_area')
        print('subset done')
        if "Tasking" in quote_type:
    #         if max(gdfbuff['area'].values) >=20:
    #             radius=100
    #             buffer_interval=buffer_interval+2
    #         if max(gdfbuff['area'].values) >=24:
    #             radius=50
    #             buffer_interval=buffer_interval+1
            buffer_interval=buffer_interval+1

        elif "Archive" in quote_type:
            print('archive')


    #             if min(gdfbuff['area'].values) >=0.95:
    #                 radius=10
    #                 buffer_interval=buffer_interval+0.025
    #                 print('0.95')
    #             elif min(gdfbuff['area'].values) >=0.8:

    #                 radius=25
    #                 buffer_interval=buffer_interval+0.1
    #                 print('0.8')
            #else:
            buffer_interval=buffer_interval+0.2

            print(f'new interval is {buffer_interval}')

        else: 
            buffer_interval=buffer_interval+0.2

        

    else:
        print("interval too big")

    return gdfbuff   

def EAProject_BuffersSubset(gdf,radius,buffer_interval,minimum_area):
    for row in gdf.itertuples():
        print(getattr(row,'Index'))
    #for cur_row in range(len(gdf)):
        original_radius=radius
        #print(cur_row)
        #cur_row_gdf=gdf.iloc[[cur_row]]
        
        geom=getattr(row,'geometry') #cur_row_gdf['geometry'][cur_row]
        #print(geom)
        
        ########### project ######
        
#         if 'area' not in gdf.columns:
#             print('area has not been calculated')
        wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')

        if geom.geom_type in ['Polygon','MultiPolygon']:
            _lon, _lat = geom.centroid.coords[0]

            #cent=gdfpol.centroid #Note this logic hasn't been tested yet.
            print('poly')
        elif geom.geom_type in ['Point']:
            #print('point')
            _lon, _lat = geom.centroid.coords[0]
            #print(pol.coords)

        wgs84_globe = pyproj.Proj(proj='longlat', ellps='WGS84')

        aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=_lat, lon_0=_lon)

        projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), geom)
        #geomlist.append(projpol)

        ####### Create dataframe from the projected data ########

        areagdf=gpd.GeoDataFrame(geometry=[projpol])
        
        print(f'the area dataframe is {areagdf}')

        ####### Calculate Area ######


        areax=areagdf.area[0]
        areakm=areax/1000000
        areagdf=areagdf.assign(area=areakm)

        

        ###### Return the area ####

        areacol=areakm
        print(f'area has been calculated and orig is {areacol}')
        
#         else:
            
#             areacol=cur_row_gdf[areavalue][cur_row]
#             print(f'area existed and orig is {areacol}')
        
        
        wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')
        # while the area of the current row is <0.1, continue iterating
        
        #if 'new_area' in gdf.columns:
            #pass
        #else:
            #gdf['new_area']=0
            
        #gdf.at[getattr(row,'Index'),'new_area']=areakm        #gdf.loc[[cur_row],'new_area']=gdf[areavalue][cur_row]
        
        while areacol <= buffer_interval:
            print('triggered buffering')               
#             else:
#                 pass
            ###### Project and Buffer #######
                
        
            if geom.geom_type in ['Polygon','MultiPolygon']:
                _lon, _lat = geom.centroid.coords[0]

                print(f'start area {areacol}')
            elif geom.geom_type in ['Point']:
                print('point')
                _lon, _lat = geom[cur_row].centroid.coords[0]

            aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=_lat, lon_0=_lon)
            
            projpol2 = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), geom)
            
            #Reduce radus if close to target minimum_area
            
            if areacol >= 0.9*minimum_area:
                radius=0.075*deepcopy(radius)
            elif areacol >= 0.7*minimum_area:
                radius=0.3*deepcopy(radius)
            else:
                pass
            
            buffpol=projpol2.buffer(radius)

            ##### Create dataframe with buffered geometry #####
            areagdf2=gpd.GeoDataFrame(geometry=[buffpol])
            ##### Calculate area and assign to gdf ####
            areax=areagdf2.area[0]
            areakm=areax/1000000
            print(f'area in km is {areakm}')
            #areagdf=areagdf.assign(area=areakm)

            ##### Project buffer back to WGS1984 ####

            output=sh_transform(partial(pyproj.transform, aeqd, wgs84_globe),buffpol)

            ##### Update original gdf #######
            if 'new_area' in gdf.columns:
                pass
            else:
                gdf['new_area']=0.0
            gdf.at[getattr(row,'Index'),'new_area']=areakm #gdf.loc[[cur_row],'geometry'] = output
            gdf.at[getattr(row,'Index'),'geometry']= output#gdf.loc[[cur_row],'geometry'] = output


            areacol=areakm
         
            geom=output #cur_row_gdf['geometry'][cur_row]
            radius=original_radius


            
            
        else:
            print(f"no geometry is smaller than current interval {buffer_interval}")
            
        
    
    return gdf

def EAProject_BuffersSubset_Sep1(gdf,radius,buffer_interval,minimum_area):

    for cur_row in range(len(gdf)):

        print(cur_row)
        cur_row_gdf=gdf.iloc[[cur_row]]
        
        geom=cur_row_gdf['geometry'][cur_row]
        #print(geom)
        
        ########### project ######
        wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')

        if geom.geom_type in ['Polygon','MultiPolygon','LineString']:
            _lon, _lat = geom.centroid.coords[0]
            
            #cent=gdfpol.centroid #Note this logic hasn't been tested yet.
            print('poly')
        elif geom.geom_type in ['Point']:
            #print('point')
            _lon, _lat = geom.centroid.coords[0]
            #print(pol.coords)

        wgs84_globe = pyproj.Proj(proj='longlat', ellps='WGS84')

        aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=_lat, lon_0=_lon)

        projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), geom)
        #geomlist.append(projpol)
        
        ####### Create dataframe from the projected data ########
        
        areagdf=gpd.GeoDataFrame(deepcopy(cur_row_gdf),geometry=[projpol])
        
        ####### Calculate Area ######
        

        areax=areagdf.area[cur_row]
        areakm=areax/1000000
        areagdf=areagdf.assign(area=areakm)

        
        ###### Return the area ####
        
        areacol=areakm
        print(f'the og area is {areacol}')
        
        
        wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')
        # while the area of the current row is <0.1, continue iterating
        while areacol <= buffer_interval:
#             if areacol >= (0.8*minimum_area):
#                 original_minimum=deepcopy(minimum_area)
#                 original_radius=deepcopy(radius)
#                 minimum_area = minimum_area*0.5
#                 radius=radius*0.5
                
#             else:
#                 pass
            ###### Project and Buffer #######
            if geom.geom_type in ['Polygon','MultiPolygon','Linestring','MultiLinestring']:
                _lon, _lat = geom.centroid.coords[0]

                print(f'start area {areacol}')
            elif geom.geom_type in ['Point']:
                print('point')
                _lon, _lat = geom[cur_row].centroid.coords[0]

            aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=_lat, lon_0=_lon)
            geom=gdf.geometry[cur_row]
            projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), geom)

            if areacol >= 0.85*minimum_area:
                original_radius=radius
                radius=0.5*deepcopy(radius)
            else:
                pass
            
            buffpol=projpol.buffer(radius)

            ##### Create dataframe with buffered geometry #####
            areagdf=areagdf.assign(geometry=[buffpol])
            
            #areagdf=gpd.GeoDataFrame(deepcopy(cur_row_gdf),geometry=[buffpol])

            ##### Calculate area and assign to gdf ####
            areax=areagdf.area
            areakm=areax/1000000
            print(f'area in km is {areakm}')
            #areagdf=areagdf.assign(area=areakm)

            ##### Project buffer back to WGS1984 ####

            output=sh_transform(partial(pyproj.transform, aeqd, wgs84_globe),buffpol)

            ##### Update original gdf #######

            gdf.loc[[cur_row],'geometry'] = output
            print(f'cur row is {cur_row}')
            ##### Create  new GDF from cur_row gdf with wgs84 buffer ####
            #buffgdf=gpd.GeoDataFrame(cur_row_gdf,geometry=[output])
            #buffgdf=buffgdf.reset_index(drop=True)
            #areagdf=aoi_areakm(buffgdf)

            ##### Update gdf with area ####
            gdf.loc[[cur_row],'area']=areakm
            ##### Update cur row gdf with area ####
            cur_row_gdf.loc[[cur_row],'area']=areakm

            areacol=gdf['area'][cur_row]
            print(f'this is the area {areacol},{gdf["area"][cur_row]}')
            #geom=gdf.geometry[cur_row]
            cur_row_gdf=gdf.iloc[[cur_row]]
            
            try:
                minimum_area=original_minimum
                radius=original_radius

            except:
                pass
            
            
        else:
            print("no geometry is too small")
            
        
    
    return gdf


def EAProject_BuffersSubset_old(gdf,radius,minimum_area=0.1):

    for cur_row in range(len(gdf)):
        print(cur_row)
        cur_row_gdf=gdf.iloc[[cur_row]]
        geom=cur_row_gdf.geometry[0]
        curarea=aoi_areakm(cur_row_gdf)
        areacol=curarea['area'][cur_row]
        wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')
        # while the area of the current row is <0.1, continue iterating
        while areacol <= minimum_area:
            

            if geom.geom_type in ['Polygon','MultiPolygon','LineString','MultiLinestring']:
                _lon, _lat = geom.centroid.coords[0]

                print(f'start area {areacol}')
            elif geom.geom_type in ['Point']:
                print('point')
                _lon, _lat = geom[cur_row].centroid.coords[0]

            aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=_lat, lon_0=_lon)

            projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), geom)

            buffpol=projpol.buffer(radius)

            output=sh_transform(partial(pyproj.transform, aeqd, wgs84_globe),buffpol)
            
            gdf.loc[[cur_row],'geometry'] = output
            buffgs=gpd.GeoSeries(output)
            buffgdf=gpd.GeoDataFrame(cur_row_gdf,geometry=buffgs)
            areagdf=aoi_areakm(buffgdf)
            #cur_row_gdf=gdf.iloc[[cur_row]]
            #geom=gdf.geometry[cur_row]
            gdf.loc[[cur_row],'area']=areagdf['area'][cur_row]

            areacol=gdf['area'][cur_row]
            print(f'{areacol},{areagdf["area"]}')

        else:
            print("no geometry is too small")

    return gdf
    
# def EAPGrid(gdf,area):
    

#     #Create Centroid for projection - this assumes that the index of the item is 0 and there is only 1 AOI polygon is being added OR it is being passed a new iloc gdf.
#     if gdf.geom_type[0] in ['Point','Polygon', 'MultiPolygon']:
#         pol2=gdf.centroid[0]
#         pass
#     else:
#         print("not valid geometry")

#     #print(pol2)
#     wgs84_globe = pyproj.Proj(proj='longlat', ellps='WGS84')

#     aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=pol2.y, lon_0=pol2.x)

#     projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), gdf['geometry'][0])    
#     temp=gpd.GeoSeries(projpol)
#     boundary=temp.bounds
      
#     poly_geometry = [
#                 (boundary['minx'][0], boundary['miny'][0]),
#                 (boundary['minx'][0], boundary['maxy'][0]),
#                 (boundary['maxx'][0], boundary['maxy'][0]),
#                 (boundary['maxx'][0], boundary['miny'][0]),
#                 (boundary['minx'][0], boundary['miny'][0]),
#                 ]
      

#     #gridx=['maxx'][0]-['minx'][0]
#     #gridy=['maxy'][0]-['miny'][0]

#     val_range = range(0,12)
#     polygons = []
    
#     area = area
#     step=1000

#     for idx in val_range:
#         print(idx)
#         width = (math.sqrt(area))
#         height = (math.sqrt(area)-width)
#         height = area/width
#         print(f"x: {width} y: {height} area: {width*height}")



#     #height = resolution
#     #width = resolution

#         cols = list(np.arange(boundary['minx'][0], boundary['maxx'][0] + width, width))
#         rows = list(np.arange(boundary['miny'][0], boundary['maxy'][0] + height, height))
#         polyproj=[]
#         for x in cols[:-1]:
#             for y in rows[:-1]:
                
#                 newpoly=(Polygon([(x,y), (x+width, y), (x+width, y+height), (x, y+height)]))
#                 newpolypro=(sh_transform(partial(pyproj.transform, aeqd, wgs84_globe), newpoly))
#                 polyproj.append(newpolypro)
                        
#                 #print(polyproj)
#         gdfname=gpd.GeoDataFrame(geometry=polyproj)
#         print(gdfname)                
#         polygons.append(gdfname)
            
#     #polyGS[x]=gpd.GeoDataFrame(geometry=polygons)

#     return polygons
#     #return polyGS

# def EAPGrid_Overlap(gdf,resolution):
#     points=[]

#     #Create Centroid for projection - this assumes that the index of the item is 0 and there is only 1 AOI polygon is being added
#     if gdf.geom_type[0] in ['Point','Polygon', 'MultiPolygon']:
#         pol2=gdf.centroid[0]
#         pass
#     else:
#         print("not valid geometry")

#     #print(pol2)
#     wgs84_globe = pyproj.Proj(proj='longlat', ellps='WGS84')

#     aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=pol2.y, lon_0=pol2.x)

#     projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), gdf['geometry'][0])    
#     temp=gpd.GeoSeries(projpol)
#     boundary=temp.bounds
      
#     poly_geometry = [
#                 (boundary['minx'][0], boundary['miny'][0]),
#                 (boundary['minx'][0], boundary['maxy'][0]),
#                 (boundary['maxx'][0], boundary['maxy'][0]),
#                 (boundary['maxx'][0], boundary['miny'][0]),
#                 (boundary['minx'][0], boundary['miny'][0]),
#                 ]
      

#     length = resolution
#     wide = resolution

#     cols = list(np.arange(boundary['minx'][0], boundary['maxx'][0] + wide, wide))
#     rows = list(np.arange(boundary['miny'][0], boundary['maxy'][0] + length, length))

#     polygons = []


#     for x in cols[:-1]:
#         for y in rows[:-1]:
#             newpoly=(Polygon([(x,y), (x+wide, y), (x+wide, y+length), (x, y+length)]))
#             newpolypro=(sh_transform(partial(pyproj.transform, aeqd, wgs84_globe), newpoly))
#             polygons.append(newpolypro)
            
#     polyGS=gpd.GeoDataFrame(geometry=polygons)

#     return polyGS
# # In[217]:


def get_boundary(geodataframe):
    #needs to be passed a geo
    temp=gpd.GeoSeries(geodataframe)
    boundary=temp.bounds
    return boundary

def polygon_from_bounds(boundary):
    poly_geometry = [
                 (boundary['minx'][0], boundary['miny'][0]),
                 (boundary['minx'][0], boundary['maxy'][0]),
                 (boundary['maxx'][0], boundary['maxy'][0]),
                 (boundary['maxx'][0], boundary['miny'][0]),
                 (boundary['minx'][0], boundary['miny'][0]),
                ]
    return Polygon(poly_geometry)


# In[218]:



# In[219]:


# In[228]:


#Outputs individual files for each feature in current working directory in a subfolder called Data. If there is a Name field, will name using it.
def output_multiAOI(gdf,output,colname):
    for cur_row in range(len(gdf)):
        #makes a subset dataframe based on current row
        cur_row_gdf = gdf.iloc[[cur_row]]
        #Create unique path
        #cwd = os.getcwd()
        #Output if no "Name"
        if colname in gdf.columns:
            filename=list(cur_row_gdf[colname])[0]
            path='{}_{}.geojson'.format(output,gdf[colname][cur_row],cur_row)
        else:
            path='{}_{}.geojson'.format(output, cur_row)
            
        data=cur_row_gdf.to_json()
        
        data = json.loads(data).get('features')[0]
         
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print("file output to {}".format(path))

def output_FeatureCollection(gdf,output):
    #cwd=os.getcwd()
    path='{}.geojson'.format(output)
    data=gdf.to_json()
    data2 = json.loads(data)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data2, f, ensure_ascii=False, indent=4)   

def GridinAOI(gdf,grid):
    gdf=gdf.set_crs(4326)
    grid=grid.set_crs(4326)

    gdfgs=gdf['geometry']
    gridgs=grid['geometry']

    
    intersect=gridgs.intersection(gdf['geometry'][0])
    
    return intersect
# In[ ]:



def aoi_areakm(gdf,column_name):
    #geomlist=[]
    #If the dataframe has been edited, this has issues (sees the geometry as nested and requires an extra positional)
    #Takes a geodataframe
    #If the dataframe has been edited, this has issues (sees the geometry as nested and requires an extra positional)
    #Takes a geodataframe
    if column_name in gdf.columns: 
        pass
    else:
        gdf.insert(loc=1, column=column_name,value=0.00)
       
    for row in gdf.itertuples():

        geom=getattr(row,'geometry')
        #for projection
        wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')

        if geom.geom_type in ['Polygon','MultiPolygon','LineString','MultiLinestring','Point']:
            _lon, _lat = geom.centroid.coords[0]

        wgs84_globe = pyproj.Proj(proj='longlat', ellps='WGS84')

        aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=_lat, lon_0=_lon)

        projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), geom)


        areagdf=gpd.GeoDataFrame(geometry=gpd.GeoSeries(projpol))

        areax=areagdf.area[0]
        areakm=areax/1000000
        gdf.at[getattr(row,'Index'),column_name]=areakm
    return gdf
        #gdf.loc[[cur_row], 'area']=areakm
        

def create_search(location,start_date,end_date,api_key,resolution,coverage):
    '''This function takes in a GeoJSON-formated polygon, a start date, an end date, and an EC API key.
    This will use EC's Search API to poll for high resolution archive data. It returns the search ID
    '''
    
    template = { "location": { "type": "Polygon", "coordinates": [ [ [ 15.992038, 29.219 ], [ 19.006121, 48.211319 ], [ 162.006121, 29.204986 ], [ 55.992038, 13.204986 ], [-1915.992038, 79.211319 ] ] ] }, "start_date": "2019-01-01", "end_date": "2020-09-29", "resolution": "low", "coverage": "0","order_by":["coverage", "resolution", "cost"]
}
    
    template["location"]["coordinates"] = location
    template["start_date"] = start_date
    template["end_date"] = end_date
    template["resolution"]=resolution
    template["coverage"]=coverage

    
    url = "https://api.skywatch.co/earthcache/archive/search"

    headers = {
    "x-api-key": api_key,
     "Content-Type": 'application/json'
    }

    # POST the search
    post_response = requests.request("POST", url, headers=headers, data = json.dumps(template))

    while post_response.status_code == "429": # watch out for clobbering the API
        print("Process being throttled - scale back!") # tell the user
        time.sleep(2)
        post_response = requests.request("POST", url, headers=headers, data = json.dumps(template))
    if post_response.status_code == "400":
        print(response.json()) # This shouldn't happen, but it'll tell you if it gets rejected. Should probably handle 500s too.
    
    body = post_response.json()
    
    return body
def get_search_results(api_key,searchid):
    
    #url = "https://api.skywatch.co/earthcache/archive/search"

    headers = {
     'x-api-key': api_key,
     'Content-Type': 'application/json'
    }
    
    get_url = "https://api.skywatch.co/earthcache/archive/search/%s/search_results" % searchid#body["data"]["id"] # uses ID from posted search
    
    get_payload  = {}
        
    time.sleep(1) # give the search some time to populate

    resultslist=[]    
    
    search_results = requests.request("GET", get_url, headers=headers,data = get_payload).json() # GET the results
    

    try:
        while search_results["status"] == [{'message': 'Search is still running. Check back later for results'}] or search_results.status_code == "429": # if results aren't ready or getting throttled
            
            search_results = requests.request("GET", get_url, headers=headers, data = get_payload).json()
            time.sleep(2)
    
    except KeyError: # The status is gone
        time.sleep(1)
        pass
    #print(search_results)
    if search_results.get('data'):
        resultslist=[]  
        resultslist.extend(search_results['data'])
        print(f'skywatch.py there are {len(resultslist)} results')
        #print(search_results)

        if len(resultslist)>0:
            #print(search_results)
            print(f"results added from first result")
            #keeplooping=True
            #count=50

            pageresults=search_results.get('pagination',{}).get('cursor',{}).get('next')
            #pageresults=search_results.get('pagination',None)
            #It is running an extra time and setting the list to []?
            while pageresults != None:
                #print(search_results.get('pagination',None))
                cursor = search_results['pagination']['cursor']['next']
                print(cursor)
                time.sleep(0.5)
                search_results = requests.request("GET", get_url, headers=headers, data=get_payload,params={"cursor":cursor}).json()
                #print(search_results.get())
                #print(search_results.get('pagination',None))
                count=1

                while not search_results or type(search_results) is "NoneType":
                    search_results = requests.request("GET", get_url, headers=headers, data=get_payload,params={"cursor":cursor}).json()
                    time.sleep(0.3)
                    count = count+1
                    if count>=10:
                        break
                    else:
                        pass

                # try:
                #     while search_results["status"] == [{'message': 'Search is still running. Check back later for results'}] or search_results.status_code == "429": # if results aren't ready or getting throttled
                #         time.sleep(2)
                #         search_results = requests.request("GET", get_url, headers=headers, data = get_payload,params={"sort":"desc","cursor":cursor}).json()


                # #print()
                # except KeyError: # The status is gone
                #     pass
                #     print('more results added')
                if search_results.get('data'):
                    #print(search_results.get('data'))
                    resultslist.extend(search_results.get('data')) 
                    print('more results added')
                    pageresults=search_results.get('pagination',{}).get('cursor',{}).get('next')
                    print(len(resultslist))
                else:
                    print('results did not return')
                    print(f'message is {search_results}')
                    pass

            return resultslist

                #pageresults=search_results.get('pagination',{}).get('cursor',{}).get('next',False)


        else:
            resultslist=[1]
            print(search_results.json())
            return resultslist
            
    else:
        resultslist=[1]
        print(search_results.json())
        return resultslist
def get_search_results_old(api_key,searchid):
    
    #url = "https://api.skywatch.co/earthcache/archive/search"

    headers = {
     'x-api-key': api_key,
     'Content-Type': 'application/json'
    }
    
    get_url = "https://api.skywatch.co/earthcache/archive/search/%s/search_results" % searchid#body["data"]["id"] # uses ID from posted search
    
    get_payload  = {}
        
    time.sleep(7) # give the search some time to populate

    resultslist=[]    
    
    search_results = requests.request("GET", get_url, headers=headers,data = get_payload).json() # GET the results
    
    try:
        while search_results["status"] == [{'message': 'Search is still running. Check back later for results'}] or search_results.status_code == "429": # if results aren't ready or getting throttled
            
            search_results = requests.request("GET", get_url, headers=headers, data = get_payload).json()
    
    except KeyError: # The status is gone
        time.sleep(1)
        pass
    #print(search_results)
    if search_results.get('data'):
        resultslist=[]  
        resultslist.extend(search_results['data'])
        print(f'skywatch.py there are {len(resultslist)} results')
        #print(search_results)

        if len(resultslist)>0:
            #print(search_results)
            print(f"results added from first result")
            #keeplooping=True
            #count=50

            pageresults=search_results.get('pagination',{}).get('cursor',{}).get('next')
            #pageresults=search_results.get('pagination',None)
            #It is running an extra time and setting the list to []?
            while pageresults != None:
                print(search_results.get('pagination',None))
                cursor = search_results['pagination']['cursor']['next']
                print(cursor)
                search_results = requests.request("GET", get_url, headers=headers, data=get_payload,params={"cursor":cursor}).json()
                #print(search_results)
                #print(search_results.get('pagination',None))
                try:
                    while search_results["status"] == [{'message': 'Search is still running. Check back later for results'}] or search_results.status_code == "429": # if results aren't ready or getting throttled
                        time.sleep(2)
                        search_results = requests.request("GET", get_url, headers=headers, data = get_payload,params={"sort":"desc","cursor":cursor}).json()


                #print()
                except KeyError: # The status is gone
                    pass
                    print('more results added')
                
                resultslist.extend(search_results.get('data')) 
                print('more results added')
                pageresults=search_results.get('pagination',{}).get('cursor',{}).get('next')
                print(len(resultslist))

            return resultslist

                #pageresults=search_results.get('pagination',{}).get('cursor',{}).get('next',False)


        else:
            resultslist=[1]
            return resultslist
    else:
        resultslist=[1]
        return resultslist
           


#####
def get_search_results_json(api_key,searchid,cursor):#Not built yet. Place holder for one that returns the search AOIs. 
    
    url = "https://api.skywatch.co/earthcache/archive/search"

    headers = {
     'x-api-key': api_key,
     'Content-Type': 'application/json'
    }
    
    get_url = "https://api.skywatch.co/earthcache/archive/search/%s/search_results" % searchid#body["data"]["id"] # uses ID from posted search

    
    get_payload  = {}
    
    
    time.sleep(7) # give the search some time to populate
    
    
    
    
    search_results = requests.request("GET", get_url, headers=headers, data = get_payload).json() # GET the results
    resultslist
    
    try:
        while results["status"] == [{'message': 'Search is still running. Check back later for results'}] or search_results.status_code == "429": # if results aren't ready or getting throttled
            time.sleep(2)
            search_results = requests.request("GET", get_url, params=params, headers=headers, data = get_payload)
            results = search_results.json()
    except KeyError: # The status is gone
        pass
    
    return results

def calc_price(coords,api_key,start,end,interval,resolution,tasking=False):
    ''' This function takes the included start & end dates, interval, and AOI,
    and returns the max_cost parameter for pipeline creation.
    
    Note that this function does not consider resolution. To add this functionality,
    you'll need another parameter in the function to use to change the "resolution"
    and "tasking" parameters from the above template.'''
    template2= {
    "interval": "7d",
    "start_date": "2021-03-15",
    "end_date": "2021-04-08",
    "location": {
        "type": "Polygon",
        "coordinates": [
            [
            ]
        ]
    },
    "resolution": "high",
    "tasking": False
    }
    
    
    updated = deepcopy(template2)
    url = "https://api.skywatch.co/earthcache/price/calculate"
    updated["location"]["coordinates"] = coords # This is assuming that coords are the
                                                # coordinates from a regular polygon in GeoJSON format
    updated["start_date"] = start
    updated["end_date"] = end
    updated["interval"] = interval
    updated['tasking']=tasking
    updated['resolution']=resolution
    
    payload = json.dumps(updated)
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    #if response.status_code == 200:
    print(response)
    return response.json()["data"]["max_cost"]
   # else:
        #return response.json() 


def run_pipe_task(coords,api_key,interval,start,end,gdf, cur_row,tag1,tag2, resolution, tasking='False', resolution_low =1.5, resolution_high=8, sources="", min_coverage=70,priorities='"latest","highest_resolution","lowest_cost"',name="Created by Skywatch", outputid='154311a8-582a-11e7-b30d-7291b81e23e1', mosaic='off'):
    ''' This function takes the template and applies the name and coordinates
    given to it, and then submits using the given api key.
    
    Args:
    coords: A List of of a List of 2D coordinate pairs -> [[[x1,y1],[x2,y2]....]]
    template: A Dictionary containing a non-Search EarthCache pipeline config -> https://api-docs.skywatch.co/#operation/PipelineCreate
    start: A String consisting of a start date for image collection -> YYYY-MM-DD
    end: A String consisting of an end date for image collection -> YYYY-MM-DD
    interval: A String consisting of an integer and the letter 'd' indicating frequency of collection -> i.e. '4d', '24d','365d'
    
    Returns: the Pipeline ID created on EarthCache, or the error.
    
    '''
    template = {
        "name": "skywatch pipeline",
        "output": {
            
            "id":"154311a8-582a-11e7-b30d-7291b81e23e1",
            "format": "geotiff",
            "mosaic": "off"
        },
        "aoi": {
            "type": "Polygon",
            "coordinates": [
                [
                ]
            ]
        },
        "min_aoi_coverage_percentage": 70,
        "result_delivery": {
            "max_latency": "0d",
            "priorities": [
                "latest","highest_resolution","lowest_cost"
            ]
        },
        "resolution_low": 0.5,
        "resolution_high": 0.5,
        "tags": [],
        "interval":"999d",
        "sources": {
            "include": []
            }   
        }

    updated = deepcopy(template) # Deepcopy to ensure that we don't overwrite the main template
    
    url = "https://api.skywatch.co/earthcache/pipelines"
    
    updated["aoi"]["coordinates"] = coords
    updated["tags"] = [] # reset tags in the template
    updated["interval"]=interval
    if not tag1:
        pass
    else:
        updated["tags"].append({"label":tag1,"value":gdf[tag1][cur_row]})
    if not tag2:
        pass
    else: 
        updated["tags"].append({"label":tag2,"value":gdf[tag2][cur_row]})
    #updated["tags"].append({"tag2"}) # this gives a tag that is easy to search for
    #updated["tags"].append({"label":"Field","value":"{}".format(gdf['FIELD'][cur_row])})
    updated["tags"].append({"label":"Submitted By","value":"Skywatch"})
    updated["max_cost"] = calc_price(coords,api_key,start,end,interval,resolution,tasking)
    updated["start_date"] = start
    updated["end_date"] = end
    updated["name"]=name
    if sources:
        updated["sources"]["include"]=[sources]
    else:
        updated.pop('sources')
    updated["resolution_low"]=resolution_low
    updated["resolution_high"]=resolution_high
    updated["min_aoi_coverage_percentage"]=min_coverage
    updated["result_delivery"]["priorities"]=priorities
    updated["output"]["id"]= outputid
    if mosaic == 'off':
        updated["output"]["mosaic"] = 'off'
    elif mosaic == 'on':
        updated["output"]["mosaic"]= { "type": "stitched" }
    

    payload = json.dumps(updated)
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data = payload)
    if response.status_code == 201:
        return response.json()["data"]["id"]
    else:
        return response.json()


def run_pipe_search(api_key,searchid, outputid, search_result, cur_row, gdf, max_cost, mosaic, tag1, tag2, name="Submitted by Pipeline Script"):
    ''' This function takes the template and applies the name and coordinates
    given to it, and then submits using the given api key.
    
    Args:
    coords: A List of of a List of 2D coordinate pairs -> [[[x1,y1],[x2,y2]....]]
    template: A Dictionary containing a non-Search EarthCache pipeline config -> https://api-docs.skywatch.co/#operation/PipelineCreate
    start: A String consisting of a start date for image collection -> YYYY-MM-DD
    end: A String consisting of an end date for image collection -> YYYY-MM-DD
    interval: A String consisting of an integer and the letter 'd' indicating frequency of collection -> i.e. '4d', '24d','365d'
    
    Returns: the Pipeline ID created on EarthCache, or the error.
    
    '''
    template = {"output": { "id": "rgbn-a3e8-11e7-9793-ae4260ee3b4b", "format": "geotiff", "mosaic": "off" },

    "tags": [],
    "search_id": "", 
    "search_results": "", 
    "max_cost":10,

    }

    updated = deepcopy(template) # Deepcopy to ensure that we don't overwrite the main template
    
    url = "https://api.skywatch.co/earthcache/pipelines"
    
    updated["tags"].append({"label":"Submitted By","value":'Skywatch'})

    if not tag1:
        pass
    else:
        try:
            updated["tags"].append({"label":tag1,"value":gdf[tag1][cur_row]})
        except:
            updated["tags"].append({"label":'tag1',"value":tag1})
    if not tag2:
        pass
    else: 
        try:
            updated["tags"].append({"label":tag2,"value":gdf[tag2][cur_row]})
        except:
            updated["tags"].append({"label":'tag2',"value":tag2})
        #updated["tags"].append({"label":"Location","value":'{}'.format(location)})
    #updated["tags"].append({"label":"Source","value":"{}".format(product)}) # this gives a tag that is easy to search for
    #updated["tags"].append({"label":"Field","value":"{}".format(gdf['population'][cur_row])}) #TanaAg
    #updated["max_cost"] = max_cost
    updated["search_id"] = searchid
    updated["search_results"] = search_result
    updated["output"]['id']=outputid

    if mosaic == 'off':
        updated["output"]["mosaic"] = 'off'
    elif mosaic == 'on':
        updated["output"]["mosaic"]= { "type": "stitched" }
    #updated["end_date"] = end_date
    updated["name"]= name
    
    payload = json.dumps(updated)
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data = payload)
    if response.status_code == 201:
        return response.json()["data"]["id"]
    else:
        return response.json()

def run_pipe_searchtest(api_key,searchid,outputid, search_result, cur_row, gdf, max_cost, mosaic, tag1, tag2, name="Submitted by Pipeline Script"):
    ''' This function takes the template and applies the name and coordinates
    given to it, and then submits using the given api key.
    
    Args:
    coords: A List of of a List of 2D coordinate pairs -> [[[x1,y1],[x2,y2]....]]
    template: A Dictionary containing a non-Search EarthCache pipeline config -> https://api-docs.skywatch.co/#operation/PipelineCreate
    start: A String consisting of a start date for image collection -> YYYY-MM-DD
    end: A String consisting of an end date for image collection -> YYYY-MM-DD
    interval: A String consisting of an integer and the letter 'd' indicating frequency of collection -> i.e. '4d', '24d','365d'
    
    Returns: the Pipeline ID created on EarthCache, or the error.
    
    '''
    template = {"output": { "id": "rgbn-a3e8-11e7-9793-ae4260ee3b4b", "format": "geotiff", "mosaic": "off" },

    "tags": [],
    "search_id": "", 
    "search_results": "", 
    "max_cost":10,

    }

    updated = deepcopy(template) # Deepcopy to ensure that we don't overwrite the main template
    
    url = "https://api.skywatch.co/earthcache/pipelines"
    
    updated["tags"].append({"label":"Submitted By","value":'Skywatch'})

    if not tag1:
        pass
    else:
        try:
            updated["tags"].append({"label":tag1,"value":gdf[tag1][cur_row]})
        except:
            updated["tags"].append({"label":'tag1',"value":tag1})
    if not tag2:
        pass
    else: 
        try:
            updated["tags"].append({"label":tag2,"value":gdf[tag2][cur_row]})
        except:
            updated["tags"].append({"label":'tag2',"value":tag2})
    #updated["tags"].append({"label":"Source","value":"{}".format(product)}) # this gives a tag that is easy to search for
    #updated["tags"].append({"label":"Field","value":"{}".format(gdf['population'][cur_row])}) #TanaAg
    updated["max_cost"] = max_cost
    updated["search_id"] = searchid
    updated["search_results"] = search_result
    updated["output"]['id']=outputid

    if mosaic == 'off':
        updated["output"]["mosaic"] = 'off'
    elif mosaic == 'on':
        updated["output"]["mosaic"]= { "type": "stitched" }
    #updated["end_date"] = end_date
    updated["name"]= name
    
    payload = json.dumps(updated)
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    
    # response = requests.request("POST", url, headers=headers, data = payload)
    # if response.status_code == 201:
    #     return response.json()["data"]["id"]
    # else:
    #     return response.json()

    return updated

def run_pipe_test(coords,api_key,interval,start,end,gdf, cur_row,tag1,tag2, resolution, tasking='False', resolution_low =1.5, resolution_high=8, sources="", min_coverage=70,priorities='"latest","highest_resolution","lowest_cost"',name="Created by Skywatch", outputid='154311a8-582a-11e7-b30d-7291b81e23e1', mosaic='off'):
    ''' This function takes the template and applies the name and coordinates
    given to it, and then submits using the given api key.
    
    Args:
    coords: A List of of a List of 2D coordinate pairs -> [[[x1,y1],[x2,y2]....]]
    template: A Dictionary containing a non-Search EarthCache pipeline config -> https://api-docs.skywatch.co/#operation/PipelineCreate
    start: A String consisting of a start date for image collection -> YYYY-MM-DD
    end: A String consisting of an end date for image collection -> YYYY-MM-DD
    interval: A String consisting of an integer and the letter 'd' indicating frequency of collection -> i.e. '4d', '24d','365d'
    
    Returns: the Pipeline ID created on EarthCache, or the error.
    
    '''
    template = {
        "name": "skywatch pipeline",
        "output": {
            
            "id":"154311a8-582a-11e7-b30d-7291b81e23e1",
            "format": "geotiff",
            "mosaic": "off"
        },
        "aoi": {
            "type": "Polygon",
            "coordinates": [
                [
                ]
            ]
        },
        "min_aoi_coverage_percentage": 70,
        "result_delivery": {
            "max_latency": "0d",
            "priorities": [
                "latest","highest_resolution","lowest_cost"
            ]
        },
        "resolution_low": 0.5,
        "resolution_high": 0.5,
        "tags": [],
        "sources": {
            "include": []
            }   
        }

    updated = deepcopy(template) # Deepcopy to ensure that we don't overwrite the main template
    
    url = "https://api.skywatch.co/earthcache/pipelines"
    
    updated["aoi"]["coordinates"] = coords
    updated["tags"] = [] # reset tags in the template
    if not tag1:
        pass
    else:
        updated["tags"].append({"label":tag1,"value":gdf[tag1][cur_row]})
    if not tag2:
        pass
    else: 
        updated["tags"].append({"label":tag2,"value":gdf[tag2][cur_row]})
    #updated["tags"].append({"tag2"}) # this gives a tag that is easy to search for
    #updated["tags"].append({"label":"Field","value":"{}".format(gdf['FIELD'][cur_row])})
    updated["tags"].append({"label":"Submitted By","value":"Skywatch"})
    updated["max_cost"] = calc_price(coords,api_key,start,end,interval,resolution,tasking)
    updated["start_date"] = start
    updated["end_date"] = end
    updated["name"]=name
    if sources:
        updated["sources"]["include"]=[sources]
    else:
        updated.pop('sources')
    updated["resolution_low"]=resolution_low
    updated["resolution_high"]=resolution_high
    updated["min_aoi_coverage_percentage"]=min_coverage
    updated["result_delivery"]["priorities"]=priorities
    updated["output"]["id"]= outputid
    updated["output"]["mosaic"]=mosaic
     
    payload = json.dumps(updated)
    headers = {
      'x-api-key': api_key,
      'Content-Type': 'application/json'
    }
    
    # response = requests.request("POST", url, headers=headers, data = payload)
    # if response.status_code == 201:
    #     return response.json()["data"]["id"]
    # else:
    #     return response.json()
    return updated    
    
def download_file(url, name, path,pipelinename):
    '''Thanks to Roman Podlinov in https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
    
    Consumes a given URL and name, and downloads whatever is at the url to a file called name
    
    Args:
    url: A String containing a web URL -> "https://www.example.com"
    name: A String containing a filename -> "myfile.tif"
    
    Returns: the name of the file downloaded
    
    '''
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        location='{}/{}'.format(path,name)
        with open(location, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return name

def download_pipeline(pipeline, name, path, apikey):
    '''This function downloads the imagery and metadata from a pipeline to the 
    local folder. It checks to see if the GeoTIFF has already been downloaded.
    
    Args:
    pipeline: A String containing an EarthCache pipeline ID -> "UUID"
    name: A String containing a name to pre-pend to each result -> "MyName"
    api-key: A String containing your EarthCache API Key. -> "UUID"

    
    '''
    headers = {'x-api-key': apikey}
    url = "https://api.skywatch.co/earthcache/interval_results?pipeline_id=%s" % pipeline
    intervals = requests.request("GET", url, headers=headers).json()['data'] # all of the imaging windows
    print(url)
    print(len(intervals))
    for interval in intervals: # iterate through each imaging window
        #print(interval)
        resultn = 1
        for result in interval['results']: # If the image is large, it may be tiled, so we iterate through the results
            #print(result)
            analytic = result["analytics_url"] # GeoTIFF image
            visual = result["visual_url"] # Visual PNG - omit if only TIF is needed
            metadata = result["metadata_url"] # Metadata file - omit if only TIF is needed
            files = []
            for raster_file in result["raster_files"]: # find the cloud mask raster
                print("found a raster_file")
                if raster_file["name"] == "cloud_mask_raster": # Found it
                    cloudmask = raster_file["uri"]
                    files = [analytic,visual,cloudmask,metadata] # Cloud mask - omit if only TIF is needed
                    break # there should only be one cloud mask
            #newfile=
            fullpath="{}/{}".format(path,name + " " + analytic.rsplit('/', 1)[-1])
            if files == []: # there's no cloud mask
                print("files files files")
                files = [analytic,visual,metadata]
                print("files found")
            if not os.path.exists(fullpath): # check if file exists
                print("Downloading result %s from %s from pipeline %s" % (resultn,interval['interval']['start_date'],pipeline))
                for file in files:
                    download_file(file,name + " " + file.rsplit('/', 1)[-1],path,name)
            else:
                print('File has already been downloaded')
            resultn += 1

def pipeline_retrieval(apikey,searchname,path): #Can adapt easily to do based on ID, tags etc
    # GET list of pipelines from the API
    url = "https://api.skywatch.co/earthcache/pipelines"

    payload={}
    headers = {
      'x-api-key': apikey
    }
    # Send the request & check for pagination. Keep searching if there are multiple pages.
    pipelines = []
    current_set = requests.request("GET", url, headers=headers, data=payload,params={"sort":"desc"}).json()
    pipelines.extend(current_set['data'])
    while current_set['pagination']['cursor']['next'] != None:
        cursor = current_set['pagination']['cursor']['next']
        current_set = requests.request("GET", url, headers=headers, data=payload,params={"sort":"desc","cursor":cursor}).json()
        pipelines.extend(current_set['data'])
    
    # Parse the list, looking for matches.
    for pipeline in pipelines:
        print(pipeline['name'])
        if searchname in pipeline['name']: # looking for the name of the pipeline to have a match
            print('found search results {}'.format(pipeline['id']))
            pipelinename=pipeline['name']
            
            ##Check if folder exists and if not, make it
            mkdir="{}/{}".format(path,pipelinename)
            check_folder=os.path.isdir(mkdir)

            if not check_folder:
                os.makedirs(mkdir)
                print("created folder : ", mkdir)
            
                #time.sleep(10)

            else:
                print(mkdir, "folder already exists. Next")
                
            download_pipeline(pipeline['id'],pipeline['name'],mkdir,apikey)

def cleangeometry(gdf):
    
    gdf=deepcopy(gdf).drop_duplicates(subset=['geometry'], keep='first', inplace=False, ignore_index=True)
    gdf=gdf.reset_index(drop=True)
    gdf=clean_data(deepcopy(gdf))
    #Reset the index (otherwise will have 2 indices which create problems running the scripts.)
    gdf=gdf.reset_index(drop=True)
    
    uniquelist=gdf['geometry'].geom_type.unique()
    if len(uniquelist) >= 2:
        print(f'This data consists of geometry types {uniquelist}')

    geom=(gdf.iloc[[0]]).geometry
    if ['LineString','MultiLineString','Point'] in uniquelist:
        pass
    elif ['Polygon','MultiPolygon'] in uniquelist:
        
        gdf=aoi_areakm(deepcopy(gdf),'start_area')
        gdf=remove_donuts(deepcopy(gdf))        
        gdf=simply_poly(deepcopy(gdf))
        gdf=aoi_areakm(deepcopy(gdf),'cleaned_area')
        gdf=gdf.reset_index(drop=True)

    # Remove donuts from the dataset (interior polygons)

        # Drop any duplicates geometries

        
    if 'valid' in gdf.columns:
        pass
    else:
        gdf["valid"] = " "
    for row in gdf.itertuples():
        geom=getattr(row,'geometry')
        isvalid=geom.is_valid
        gdf_index=getattr(row,'Index')
        gdf.at[gdf_index,'valid'] = str(isvalid)
    

            
        if 'start_area' in gdf.columns:
            if gdf['start_area'].sum()/gdf['cleaned_area'].sum() >0.95 and gdf['start_area'].sum()/gdf['cleaned_area'].sum() <1.05:
                pass
            else:
                print(f'WARNING: AREA HAS CHANGED from {gdf["start_area"].sum()} to {gdf["cleaned_area"].sum()}')
            
            # for row in gdf.itertuples():
            #     if getattr(row,'start_area')/getattr(row,'cleaned_area') > 0.95 and getattr(row,'start_area')/getattr(row,'cleaned_area') <1.05: 
            #         pass

            #     else:
                    
                    #sys.exit('The data was cleaned up, but the area grew too much and needs to be reviewed by the Solutions Engineer')
        else: 
            pass            
             #DonutsError as e:
            #raise Exception('The data was cleaned up, but the area grew too much and needs to be reviewed by the Solutions Engineer') from e

    return gdf
    
    #return simply

def importfiles(file=''):
    
    if file == '':
        tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
        file = filedialog.askopenfilename()
        #file='/Users/katrina/Documents/Solutions/Stantec/Stantec_Buffered.geojson'
        print(file)

    else:
        pass
   
    gdf=load_file(file)
    projectiongood=projection_check(gdf)
    if projectiongood==True:
        return gdf,file
    else:
        message='projection is not WGS1984. Please re-project and try again'
        print(message)
        return message

def exportfiles(gdf,gdfclean,filename,name_field = '',html_map='No',fileout='',map_name="Archive"):
    if fileout=='':
        tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
        fileout = filedialog.askdirectory()
        filename=filename.rsplit('.',1)[0]
        filepath="{}/{}".format(fileout,f'{map_name}_{filename}')
        print(filepath)

    else:
        pass

    #If you need to output to multiple geojsons, then use this function. 
    #If it's a single feature then it doesn't matter which is used.

    if len(gdfclean)<10 and len(gdfclean)!= 1:
    #No Inputs
        #filename=filename.rsplit('.',1)[0]
        filepath=f"{fileout}/{map_name}_{filename}"
        output_multiAOI(gdfclean,filepath,name_field)
    else:
        pass
    #If you need to output to a single geojson with multiple features, then use this.
    #If it's a single feature, then it doesn't matter which is used.

    #No Inputs
    filename=filename.rsplit('.',1)[0]
    filepath=f"{fileout}/{map_name}_{filename}"
    output_FeatureCollection(gdfclean,f'{filepath}')
    print(filepath)

    if html_map=='Yes':
        if "Archive" in map_name:
            qtype="Archive"
        elif "Tasking" in map_name:
            qtype="Tasking"
        else:
            qtype=map_name
        m=create_map(gdf,gdfclean)
        m.save(f'{fileout}/{qtype}_html_map.html')


        return filepath, m

    else:
        return filepath,'nomap'


def create_map(orig_gdf,clean_gdf,popup_column=''):
    #lf.Map(center = (60, -2.2), zoom = 2, min_zoom = 1, max_zoom = 20, 
#    basemap=lf.basemaps.Esri.WorldImagery)

    start=list(orig_gdf.geometry[0].centroid.coords)

    area=start[0][1],start[0][0]
    print(start[0][1],start[0][0])

    m = folium.Map(area, zoom_start=10)

    tile = folium.TileLayer(
            tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr = 'Esri',
            name = 'Esri Satellite',
            overlay = False,
            control = True
        ).add_to(m)

    def styleback(feature):
            return {
                'color': 'Black',
                'weight': 1
            }
    def stylefront(feature):
            return {
                'color': 'Red',
                'weight': 4
            }

#     try:
#     # #Background Vector Layer
    
    data3=clean_gdf.to_json()
    data4 = json.loads(data3)
    Quote=folium.FeatureGroup(name="Quote Polygons",show=True)
    folium.GeoJson(data4, style_function=styleback).add_to(Quote)
    m.add_child(Quote)


    data=orig_gdf.to_json()
    data2 = json.loads(data)
    Original=folium.FeatureGroup(name="Original Data",show=True)
    
    if popup_column!='':
        folium.GeoJson(data2,style_function=stylefront,popup=folium.GeoJsonPopup(fields=[popup_column])).add_to(Original)
    else:
        folium.GeoJson(data2,style_function=stylefront).add_to(Original)
        m.add_child(Original)
    #folium.features.GeoJsonPopup(fields=["CLAIM_NAME"],
    #labels=True).add_to(aoi)

    folium.LayerControl().add_to(m)

    m

    return m


def corridor_quote(gdf, quote_type,resolution, buffer_type,buffer_amount,):
    uniquelist=gdf['geometry'].geom_type.unique()
    if['MultiLineString', 'LineString'] in uniquelist:
        print(f'The file contains datatypes {uniquelist}')
    else:
        print(f'This data consists of geometry types {uniquelist} which cannot be used for the corridor analysis.')
        print(f'To proceed, get Line data from the customer')
              
    gdfclean=cleangeometry(deepcopy(gdf))
    if quote_type == "Archive" and resolution == "medium":
        if buffer_type == 'radius'and buffer_amount >=50:
            pass
        else:
            buffer_amount=50
            print(f'buffer amount was set to 50 as this is the minimum for this quote')
        
    elif quote_type == "Archive" and (resolution == "high" or resolution == "very_high"):
        if buffer_type == 'radius'and buffer_amount >=50:
            pass
        else:
            buffer_amount=50
            print(f'buffer amount was set to 50 as this is the minimum for this quote')
                     
    elif quote_type == "Tasking" and resolution == "high":
        if buffer_type == 'radius'and buffer_amount >=250:
            pass
        else:
            buffer_amount=250
            print(f'buffer amount was set to {buffer_amount} as this is the minimum for this quote')
    elif quote_type == "Tasking" and resolution == "very_high":
        if buffer_type == 'radius'and buffer_amount >=1000:
            pass
        else:
            buffer_amount=1000
            print(f'buffer amount was set to 250 as this is the minimum for this quote')
    else:
        print('quote type not valid')
        exit()

    if buffer_type == 'radius':
        gdfbuff=EAProject_Buffer(deepcopy(gdfclean),buffer_amount,capstyle=1)
        gdfbuff=gdfbuff.dissolve()
        gdfbuff=gdfbuff.explode()
        gdfbuff=gdfbuff.reset_index(drop=True)
        gdfbuff=aoi_areakm(gdfbuff,'optimized_area')
        #gdfbuffclean=cleangeometry(gdfbuff)
    elif buffer_type== 'area':
        print('cannot buffer corridors using area. Please set a radius.')

    gdfbuff=optimize_area(deepcopy(gdfbuff), quote_type, resolution, 1000000)

    return gdfbuff

def optimize_area_report(gdfclean,quote_type,data_type,resolution,minarea,detail,filepath=''):
    dfquote=pd.DataFrame(columns=['State','Number of Features','Total Area','Average Area per feature','Quote Type'])
    #gdfclean=EAProject_Buffer(gdfclean,10,capstyle=1)
    gdfclean=aoi_areakm(gdfclean,'optimized_area') 
    
    bufferedtext='Area of data after geometry cleaning'
    try:
        len_features=gdfclean.index.stop
    except:
        len_features=1
    avgarea=int(gdfclean['optimized_area'].sum())/int(len_features)
    dfquote2=pd.DataFrame([[bufferedtext,len_features,gdfclean['optimized_area'].sum(),avgarea,quote_type]],columns=dfquote.columns)
    dfquote=dfquote.append(dfquote2)
    print(dfquote)
    print(dfquote.columns)
    if quote_type == "Tasking":
        radius=200  #radius to buffer in iteration (in m)
        print(f'Tasking')
        if minarea <25000000:
            minarea=25
            radius=200  #radius to buffer in iteration (in m)
            buffer_interval=1
            start_interval=buffer_interval
            print(f'Tasking buff int is {buffer_interval}')
        else:
            minarea=minarea/1000000
            #buffer_interval=minarea/
            if minarea%5==0:
                buffer_interval=5
            elif minarea%3==0:
                buffer_interval=3
            elif minarea%2==0:
                buffer_interval=2
            elif minarea%1==0:
                buffer_interval=1
            else:
                print('area must be a whole number')
                exit()
            start_interval=buffer_interval
        #minarea=25# minimum area to hit (in km2)
        
    #else:    
    elif 'Archive' in quote_type:
        radius=25
        #minarea=1
        print(f"Archive optimization beginning for {resolution}")
        if minarea <=1000000:
            minarea=1
            radius=25  #radius to buffer in iteration (in m)
            if detail=='low':
                buffer_interval=1
                radius=75
            elif detail=='medium':
                buffer_interval=0.5
                radius=50
            else:
                buffer_interval=0.2
            start_interval=buffer_interval
            print(buffer_interval)
        else:
            minarea=minarea/1000000
            if minarea<3:
                buffer_interval=0.2
            else:
                buffer_interval=minarea/10
            print(buffer_interval)
            start_interval=buffer_interval
    
#     elif quote_type == "Archive Med Res":
#         if minarea <1000:
#             minarea=0.1
#             radius=50  #radius to buffer in iteration (in m)
#             buffer_interval=0.05
#         else:
#             minarea=minarea/1000000
#             buffer_interval=minarea/5

    else: 
        print('quote type does not match options.')
        sys.exit('quote type does not exist')

    print(f'buffer_interval is {buffer_interval}')        
    gdfbuff=gpd.GeoDataFrame(deepcopy(gdfclean))


    while buffer_interval <= minarea: # while 0.4 <= 1
        print(f'minimum area value is {min(gdfbuff["optimized_area"].values)}')
        #while (min(gdfbuff['area'].values))<= buffer_interval: # if min gdf area < 1
        #while buffer_interval < minarea:
        print(f'interval buffer is {buffer_interval}')
        print(f'minimum area is {min(gdfbuff["optimized_area"].values)}')
        if min(gdfbuff["optimized_area"].values) < buffer_interval:
            gdfbuff=EAProject_BuffersSubset(deepcopy(gdfbuff),radius,buffer_interval,minarea)
            gdfbuff=gdfbuff.dissolve()
            gdfbuff=gdfbuff.explode()
            gdfbuff=gdfbuff.reset_index(drop=True)
            if quote_type != 'Corridors':
                
                gdfbuff=remove_donuts(deepcopy(gdfbuff))
            else:
                pass
            
            #gdfbuff=sw.aoi_areakm(gdfbuff,'tasking_area')
            print('subset done')
            if "Tasking" in quote_type:
        #         if max(gdfbuff['area'].values) >=20:
        #             radius=100
        #             buffer_interval=buffer_interval+2
        #         if max(gdfbuff['area'].values) >=24:
        #             radius=50
        #             buffer_interval=buffer_interval+1
                buffer_interval=buffer_interval+start_interval

            elif "Archive" in quote_type:
                print('archive')


        #             if min(gdfbuff['area'].values) >=0.95:
        #                 radius=10
        #                 buffer_interval=buffer_interval+0.025
        #                 print('0.95')
        #             elif min(gdfbuff['area'].values) >=0.8:

        #                 radius=25
        #                 buffer_interval=buffer_interval+0.1
        #                 print('0.8')
                #else:
                buffer_interval=buffer_interval+start_interval

                print(f'new interval is {buffer_interval}')

            gdfbuff=aoi_areakm(gdfbuff,'optimized_area') 

        else: 
            print('no area smaller than interval')
            buffer_interval=buffer_interval+start_interval
            print(f'new interval is {buffer_interval}')
            gdfbuff=aoi_areakm(gdfbuff,'optimized_area') 
            
        bufferedtext=f'Each feature buffered to {round(buffer_interval-start_interval,1)}km2'
        try:
            len_features=gdfbuff.index.stop
        except:
            len_features=1
        avgarea=int(gdfbuff['optimized_area'].sum())/int(len_features)
        newdfquote=pd.DataFrame([[bufferedtext,len_features,gdfbuff['optimized_area'].sum(),avgarea,quote_type]],columns=dfquote.columns)
        dfquote=dfquote.append(newdfquote,ignore_index=True)
        if quote_type == "Tasking":
            files=f'{filepath}/tasking_areaoutput{round(buffer_interval-start_interval,2)}'
        else:
            files=files=f'{filepath}/archive_areaoutput{round(buffer_interval-start_interval,2)}'
        print(filepath)

        #No Inputs
        if filepath != '':
            output_FeatureCollection(gdfbuff,files)
            print(files)
        else:
            pass
        
        

    else:
    
        print("interval too big")
        
    return [gdfbuff,dfquote]

def concave_optimize(gdfbuffarea,gdfgroupfinal,cluster_force=True):
#gdf_og_points=gpd.GeoDataFrame(columns=['geometry'])
    pointylist=[]
    for row in gdfbuffarea.itertuples():
        geom=getattr(row,'geometry')
        for item in geom.exterior.coords:
            pointylist.append(Point(item))
    print('creating new geodataframes')
    gs=gpd.GeoSeries(pointylist)
    gdf_og_points=gpd.GeoDataFrame(geometry=gs)
    gdf_og_points=gdf_og_points.set_crs('EPSG:4326')
    print('points created')

    #for row in gdfarea.itertuples():
        #if 

    joingdf=gpd.sjoin(gdf_og_points,gdfgroupfinal,how="left")
    #print(gdf_og_points.index[0])
    #print(joingdf.columns)
    #print(joingdf.index)

    concave_output=gpd.GeoDataFrame(columns=['geometry'])

    if 'index_right' in joingdf.columns:   
        uniquelist=joingdf['index_right'].unique()
        print(f'the uniquelist is {uniquelist}')
        
    else:
        print('index column was not created')
        sys.exit()

    for unique in uniquelist:
        print(unique)
        pointlist=[]
        subset=joingdf[joingdf['index_right']==unique]
        #print(subset.index)
        #subset=subset.reset_index(drop=True)
        #if subset['optimized_area',[0]]>=25.5:
        #if unique != nan and gdfbuff.at[round(unique),'optimized_area']>=25.5:
        
        for row in subset.itertuples():
            #print(row)
            #if getattr()
            point=getattr(row,'geometry')
            points=point.coords
            #print (points)
            #print(points[0])
            pointlist.append(points[0])
            
        print(len(pointlist))
        
        #print(pointlist[0])
        
        if len(pointlist)==0:
            pass
        #elif gdfbuff.at[round(unique),'optimized_area']>=26:
        else:

            #print(gdfbuffarea.at[round(unique),'optimized_area'])
            alphalist=[]
            #alpha = 0.95 * alphashape.optimizealpha(pointlist)
            alpha=1000
            alpha_shape = alphashape.alphashape(pointlist, alpha)
            print(alpha_shape)
            print(alpha_shape.geom_type)
            #print(len(alpha_shape.exterior.coords.xy))
            count=0
            ## len(alpha_shape) only works if it is multipart - this is why it is in a try except. This reduces alpha trying to get a single polygon.
            #for shape in 
            
            while alpha_shape.geom_type!= 'Polygon' and alpha_shape.geom_type!='MultiPolygon':
                print(type(alpha_shape.geom_type))
                alpha=alpha/2
                alpha_shape = alphashape.alphashape(pointlist, alpha)
                count=count+1
            else:
                count=0
                if cluster_force==True:
                    while alpha_shape.geom_type=='MultiPolygon' and count <= 6:
                        print(type(alpha_shape.geom_type))
                        alpha=alpha/2
                        alpha_shape = alphashape.alphashape(pointlist, alpha)
                        count=count+1
                    else:
                        if alpha_shape.geom_type=='MultiPolygon':
                            print(f'submitting as multipolygon')
                            alphalist=[]
                            for shape in alpha_shape:
                                alphalist.append(Polygon(shape))
                        else:
                            print(f'geom type is {alpha_shape.geom_type}')
                            pass
                        
                elif cluster_force==False:
                    while alpha_shape.geom_type=='MultiPolygon' and count <= 3:
                        print(type(alpha_shape.geom_type))
                        alpha=alpha/2
                        alpha_shape = alphashape.alphashape(pointlist, alpha)
                        count=count+1
                    else:
                        if alpha_shape.geom_type=='MultiPolygon':
                            print(f'submitting as multipolygon')
                            alphalist=[]
                            for shape in alpha_shape:
                                alphalist.append(Polygon(shape))
                        else:
                            print(f'geom type is {alpha_shape.geom_type}')
                            pass
                    
                    
                if alpha_shape.geom_type=='Polygon':
                    alphalist.append(alpha_shape)

                if alpha_shape.geom_type!= 'Polygon' and alpha_shape.geom_type!='MultiPolygon':
                    print('concave hull failed')

                else:
                    print('concave_hull succeeded')

                
            concave_gs=gpd.GeoSeries(alphalist)
            concave_gdf=gpd.GeoDataFrame(geometry=concave_gs)
            concave_output=concave_output.append(concave_gdf,ignore_index=True)
    return concave_output

def area_group(gdfclean,quote_type,minarea,filepath=''):
    #gdfclean=aoi_areakm(gdfclean,'optimized_area')
    if quote_type == "Tasking High Res" or quote_type == "Tasking Very High Res":
        gdfclean=EAProject_Buffer(gdfclean,5000,capstyle=1)
    elif quote_type == "Archive High Res" or quote_type == "Archive Med Res": 
        gdfclean=EAProject_Buffer(gdfclean,1000,capstyle=1)
    return gdfclean

def optimize_area_group(gdfclean,quote_type,resolution, minarea,detail,filepath=''):
    
    #New one that buffers automatically to 100km2 and makes groupings (tasking) and 5km2 (archive) and then goes straight to concave
    
    #gdfclean=EAProject_Buffer(gdfclean,10,capstyle=1)
    gdfclean=aoi_areakm(gdfclean,'optimized_area') 
    
    if quote_type == "Tasking":
        if detail == 'high':
            radius=50  #radius to buffer in iteration (in m)
            #print(f'Tasking')
            minarea=4
            #radius=300  #radius to buffer in iteration (in m)
            buffer_interval=1
            start_interval=buffer_interval
            print(f'Tasking buff int is {buffer_interval}')
        elif detail == 'medium':
            radius=100  #radius to buffer in iteration (in m)
            #print(f'Tasking')
            minarea=20
            #radius=300  #radius to buffer in iteration (in m)
            buffer_interval=2
            start_interval=buffer_interval
            print(f'Tasking buff int is {buffer_interval}')
        elif detal=='low':
            radius=200  #radius to buffer in iteration (in m)
            #print(f'Tasking')
            minarea=40
            #radius=300  #radius to buffer in iteration (in m)
            buffer_interval=4
            start_interval=buffer_interval
            print(f'Tasking buff int is {buffer_interval}')
    
    else:    
    #elif quote_type == "Archive High Res" or quote_type == "Archive Med Res":
        radius=50
        #minarea=1
        print("Archive optimization submitted")
       
        minarea=1
        radius=50  #radius to buffer in iteration (in m)
        buffer_interval=0.1
        start_interval=buffer_interval
        print(buffer_interval)
       
    

#     else: 
#         print('quote type does not match options.')
#         sys.exit('quote type does not exist')

    print(f'buffer_interval is {buffer_interval}')        
    gdfbuff=gpd.GeoDataFrame(deepcopy(gdfclean))


    while buffer_interval <= minarea: # while 0.4 <= 1
        print(f'minimum area value is {min(gdfbuff["optimized_area"].values)}')
        #while (min(gdfbuff['area'].values))<= buffer_interval: # if min gdf area < 1
        #while buffer_interval < minarea:
        print(f'interval buffer is {buffer_interval}')
        print(f'minimum area is {min(gdfbuff["optimized_area"].values)}')
        if min(gdfbuff["optimized_area"].values) < buffer_interval:
            gdfbuff=EAProject_BuffersSubset(deepcopy(gdfbuff),radius,buffer_interval,minarea)
            gdfbuff=gdfbuff.dissolve()
            gdfbuff=gdfbuff.explode()
            gdfbuff=gdfbuff.reset_index(drop=True)
            if quote_type != 'Corridors':
                
                gdfbuff=remove_donuts(deepcopy(gdfbuff))
            else:
                pass
            gdfbuff=aoi_areakm(gdfbuff,'optimized_area') 
           
        else:
            print('no area smaller than interval')

            buffer_interval=buffer_interval+start_interval

            print(f'new interval is {buffer_interval}')

    else:
    
        print("interval too big")
        
    return gdfbuff

def create_html_report(gdf,gdfbuff,quote_type,resolution,data_type,filepath,filename,buffer_amount,totalorigarea,output_chart,final_area,coverage_map,coverage_area):
    if resolution == "high":
        printres="High Resolution"
    if resolution == "very_high":
        printres="Very High Resolution"
    if resolution == "medium":
        printres="Medium Resolution"
    
    if 'Archive' in quote_type:
        page_title_text=f'Archive Quote for {filename}'
        title_text = f"{printres} Quote for {quote_type}"
        qtype="Archive"
        df2=gdfbuff[['final_area']].copy()
        df=pd.DataFrame(output_chart)
        pd.set_option('display.max_colwidth', 40)       
        df2html=df2.style.set_table_attributes('class="table-style"').to_html()
        #coverage_map =  '<embed type="text/html" src="archive_coverage_html_map.html" width="1000" height="700">'
        if data_type=="Corridors":
            text = f'This report quotes for Archive Data at a buffer of {buffer_amount}'
            dfhtml=''
            if buffer_amount <= 50:
                buffer_amount=50
            else:
                pass
        else:
            text=f''
            dfhtml = df.style.set_table_attributes('class="table-style"').to_html()
            pass
        
        if coverage_map=='Yes':
            coverage_map = f'<embed type="text/html" src="{resolution}_archive_coverage_html_map.html" width="1000" height="700">'
            coverage_title='<h1> Coverage Map for Archive Quote </h1>'
            coveragearea=f'<h2> Area of Archive Coverage is {coverage_area}</h2>'
            
        elif coverage_map=='No':
            coverage_map=''
            coverage_title='<h2>No Coverage Request</h2>'
            coveragearea=''
            
        prices_text = round(final_area,2)
        #stats_text = round(customer_price*totalbuffarea,2)

        if totalorigarea != 0:
            areatext=f'The original area was {totalorigarea}'
            
        else:
            areatext='no original area as points or lines were provided'


        #dfhtml=dfarea.to_html()

        html = f'''
            <!doctype html>
            <html lang="en">

            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Bootstrap demo</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-iYQeCzEYFbKjA/T2uDLTpkwGzCiq6soy8tYaI1GyVh/UjpbCx/TYkiZhlZB6+fzT" crossorigin="anonymous">

                    <title>{page_title_text}</title>
            </head>
            <body>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/js/bootstrap.bundle.min.js" integrity="sha384-u1OknCvxWvY5kfmNBILK2hRnQC3Pr17a+RTT6rIHI7NnikvbZlHgTPOOmMi466C8" crossorigin="anonymous"></script>
                <h1>{title_text} for {data_type}</h1>
                <p>{text}</p>
                <h2>{areatext}<h2>
                <h2>The quote area is {prices_text}km2</h2>
                <br>
                
                <h1> Output Map Showing Original Vs Quote Polygons </h1>
                
                <embed type="text/html" src="{qtype}_html_map.html" width="1000" height="700">

                {coverage_title}
                
                {coveragearea}
                <br>
                
                {coverage_map}

                {dfhtml}

            </body>
        </html>
        '''
    else:
        page_title_text=f'Tasking Quote for {filename}'
        title_text = f"{printres} Quote for {quote_type}"
        qtype="Tasking"
        df2=gdfbuff[['final_area']].copy()
        df=pd.DataFrame(output_chart)
        pd.set_option('display.max_colwidth', 40)
        dfhtml = ''
        df2html=df2.style.set_table_attributes('class="table-style"').to_html()
        if data_type=="Corridors":
            text = f'This report quotes for Archive Data at a buffer of {buffer_amount}'
            if "Very" in quote_type:
                buffer_amount=1
            else:
                buffer_amount=250
                
        else:
            text=f''
            pass
        
       
        #text = f'This report quotes for Tasking Data at a buffer of {buffer_amount}'
        prices_text = round(final_area,2)
        #stats_text = round(customer_price*totalbuffarea,2)

        if  totalorigarea != 0:
            areatext=f'The original area was {totalorigarea}'

        else:
            areatext='no original area as points or lines were provided'

       
        #dfhtml=dfarea.to_html()

        html = f'''
        <html>
            <head>

                <title>{page_title_text}</title>
            </head>
            <body>
                <h1>{title_text} for {data_type}</h1>
                <p>{text}</p>
                <h2>{areatext}<h2>
                <h2>The quote area is {prices_text}km2</h2>
                <br>

                <h1> Output Map Showing Original Vs Quote Polygons <h1>

                <embed type="text/html" src="{qtype}_html_map.html" width="1000" height="700">

                {dfhtml}

            </body>
        </html>
        '''

    with open(f'{filepath}/{printres}_{quote_type}_html_report.html', 'w') as f:
        f.write(html)
        #f.write(dfhtml)
        
    exportfiles(gdf,gdfbuff,filename,name_field = '',html_map='Yes',fileout=filepath,map_name=f'{printres}_{quote_type}')


def cleanup(gdfbuff,data_type):

    if data_type!="Corridors":
        try:
            gdfsimp=simply_poly(deepcopy(gdfbuff))
            gdfbuffarea=aoi_areakm(deepcopy(gdfsimp),'final_area')
            totalbuffarea=gdfbuffarea['final_area'].sum()
            totalbuffarea

        except:

            gdfbuffarea=aoi_areakm(deepcopy(gdfbuff),'final_area')
            totalbuffarea=gdfbuffarea['final_area'].sum()
            totalbuffarea
            
    else:
        gdfbuffarea=aoi_areakm(deepcopy(gdfbuff),'final_area')
        totalbuffarea=gdfbuffarea['final_area'].sum()
        totalbuffarea
        
            
    return gdfbuffarea,totalbuffarea

def archive_coverage(gdf,start_date,end_date,api_key,low_res,cloud,data_type,coverage_resolution,percent_coverage,filepath,alpha=12):
    searchlist=[]
    faillist=[]
    productidlist=[]
    if data_type!='Corridors' and data_type != 'Large AOI':
        try:
            gdfclean=cleangeometry(deepcopy(gdf))
            pointylist=[]
            for row in gdfclean.itertuples():
                geom=getattr(row,'geometry')
                for item in geom.exterior.coords:
                    #print (item)
                    pointylist.append(item)
            #gs=gpd.GeoSeries(pointylist)
            #gdf_og_points=gpd.GeoDataFrame(geometry=gs)
            #gdf_og_points=gdf_og_points.set_crs('EPSG:4326')
            #alpha = 0.95 * alphashape.optimizealpha(points)
            hull = alphashape.alphashape(pointylist, alpha)
            #for item in hull
                
            concave_gs=gpd.GeoSeries(hull)
            concave_gdf=gpd.GeoDataFrame(geometry=concave_gs)
            concave_gdf=cleangeometry(concave_gdf)
        except:
            print(f'Could not generate a concave hull. This search may take awhile. GDF length is {len(gdfclean)}')
            concave_gdf=deepcopy(gdf)

    else:
        gdfclean=cleangeometry(deepcopy(gdf))
        pointylist=[]
        for row in gdfclean.itertuples():
            geom=getattr(row,'geometry')
            for item in geom.exterior.coords:
                #print (item)
                pointylist.append(item)
        convex=shapely.geometry.MultiPoint(pointylist).convex_hull
        convexgs=gpd.GeoSeries(convex)
        convexgdf=gpd.GeoDataFrame(geometry=convexgs)
        
        
        
        concave_gdf=convexgdf

    
    #concave_gdf=deepcopy(gdf)
    fulfilled=0
    unfulfilled=0

    searchlist=[]
    #gdf=gdfclean.set_crs('EPSG:4326')
    #gdfsearch=gdfclean.dissolve()
    #gdfsearch=gdfsearch.explode()
    #gdfsearch=gdfsearch.reset_index(drop=True)


    for idx,cur_row in enumerate(range(len(concave_gdf))):
        print(f'this is loop {idx}')
        cur_row_gdf=concave_gdf.iloc[[cur_row]]
        new = cur_row_gdf.to_json()
        data=json.loads(new).get('features')
        data=data[0]['geometry']
        coords=data['coordinates']
        if cur_row_gdf.geometry[cur_row].is_valid:
            for idx,start in enumerate(start_date):
                end = end_date[idx]
            
                search=create_search(coords,start,end,api_key,coverage_resolution,percent_coverage)
                if 'errors' in search:
                    print('search failed on record {}'.format(cur_row))
                    print(search.get('errors'))
                    exit()
                else:
                    ########## Add resolution filter################
                    searchdata=search.get('data')
                    searchid=searchdata.get('id')
                    time.sleep(3)
                    print(f'searchid is {searchid}')
                    searchresults=get_search_results(api_key,searchid)

                if len(searchresults)>0:
                    if searchresults[0]!=1:

                        print('there are search results')
                        datacount=0

                        for data in searchresults:
                        # try:
                            if low_res == 0:
                                low_res=30
                            
                            #if data.get('source') == '' and data.get('result_cloud_cover_percentage') <=50:
                            if data.get('result_cloud_cover_percentage') <= cloud and data.get('resolution')<= low_res:


                                #if data.get('result_cloud_cover_percentage')<=10 and data.get('resolution')<=5:

                                coords=data.get('location').get('coordinates')
                                #print(f'the length of the coordinates is {len(coords)}')
                                if len(coords)==1:
                                    print(data.get('source'))
                                    searchlist.append(data)
                                    print(f'the length of the searchlist is {len(searchlist)}')


                                elif len(coords)!=1:
                                    print(f'too many coordinates, {len(coords)}')
                                    #for shape in coords:
                                    pass

                                else:
                                    faillist.append(data)
                                    print(f'this had results but they were multipolygon')


                            else:
                                print('does not meet requirements')
                                    
    #                         except:
    #                             print(f'{data.get('source')},{type(data)}')


                    else:
                        print('searchresult returned a value of 1')

                        unfulfilled=unfulfilled+1

                else:
                    print('search results not >0')
                    pass  
                    
        else:
            print(f'not valid geometry for record {cur_row}')
            pass
        
    featlist=[]

    if len(searchlist)>=1:
        print(len(searchlist))
        for data in searchlist:
            #print(data.get('geometry'))
            
    #         for item in fc.get('features'):
    #         item=item.get('geometry')
    #         for coord in item.get('coordinates'):
    #         print(len(coord))
    #         if len(coord)<5:
    #             print(item)
            date=data.get('start_time')
            collectiontime=date.split('T')[-1]
            date=date.split('T')[0]
            tpoly=geojson.Polygon(data['location']['coordinates'])
            feat = geojson.Feature(geometry=tpoly,properties={"id":data['product_name'],"cc":data['location_coverage_percentage'],"preview":data['preview_uri'],"clouds":data['result_cloud_cover_percentage'],"date":date, "resolution":data['resolution'], "source":data['source'],"bbox":data['location']['bbox']})
            featlist.append(feat)
        
            #feat['feature'].

            #gdfout=gdp.read_file(data2)
            
        fc = geojson.FeatureCollection(featlist)

        gdfout=gpd.GeoDataFrame.from_features(fc['features'])
        gdfout=gdfout.set_crs('EPSG:4326')
    
        #del cloudjoin
        gdfout=gdfout.set_crs('EPSG:4326')
        gdf=gdf.set_crs('EPSG:4326')
        cloudsortgdf=gdfout.sort_values('clouds', axis=0, ascending=False)
        cloudsortgdf=cloudsortgdf.reset_index(drop=True)

        aoiintersect=gpd.overlay(gdf, gdfout, how='intersection')
        aoiintersect=aoiintersect.dissolve()
        aoiintersect=aoiintersect.reset_index(drop=True)
        aoiintersect=aoiintersect.explode()
        aoiintersect=aoiintersect.reset_index(drop=True)
        aoiintersect=aoi_areakm(aoiintersect,'intersect_area')

        exportfiles(gdf,aoiintersect,"archive_coverage",name_field='',html_map='No',fileout=filepath,map_name='Archive Coverage')

        totalarea=aoiintersect['intersect_area'].sum()


        start=list(gdf.geometry[0].centroid.coords)

        area=start[0][1],start[0][0]
        #print(start[0][1],start[0][0])


        m = folium.Map((area), zoom_start=10)

        def styleback(feature):
                return {
                    'color': '',
                    'weight': 1
                    }
        def stylefront(feature):
                return {
                    'color': 'Red',
                    'weight': 4
                    }
        def styleintersect(feature):
            return {
                'color': 'Blue',
                'weight': 2
                }

        # aoi = folium.FeatureGroup(name="AOITop")
        # data=gdfclean.to_json()
        # data2 = json.loads(data)
        # aoi.add_child(folium.GeoJson(data2,style_function=stylefront))
        aoi = folium.FeatureGroup(name="AOI")
        data=gdfclean.to_json()
        data2 = json.loads(data)
        aoi.add_child(folium.GeoJson(data2,style_function=stylefront))
       # aoi.add_to(m)
        # m.add_child(aoi)

        imagery_group=folium.FeatureGroup('Imagery Coverage',show=True)

        for idx,cur_row in enumerate(range(len(cloudsortgdf))):
            cur_row_gdf=cloudsortgdf.iloc[[cur_row]]
            #print(cur_row)
            name=f'{idx}_{cur_row_gdf["id"][cur_row]}'
            fg2=folium.FeatureGroup(name,show=True)
            url=cur_row_gdf['preview'][cur_row]
            boundary=cur_row_gdf.bounds
            #print(boundary)
            minbounds = boundary['miny'][cur_row],boundary['minx'][cur_row]
            maxbounds= boundary['maxy'][cur_row],boundary['maxx'][cur_row]

            raster=folium.raster_layers.ImageOverlay(image=url,bounds=([minbounds,maxbounds]),opacity=1,interactive=True)
            raster.add_to(fg2)

            #raster.add_to(imagery_group)

            fg2.add_to(m)

        #imagery_group.add_to(m)
        #m.add_child(imagery_group)
        #magery_group.add_to(m)
        aoi.add_to(m)
       # m.add_child(aoi)
        m.keep_in_front(aoi)
        folium.LayerControl().add_to(m)

        m.save(f'{filepath}/{coverage_resolution}_archive_coverage_html_map.html')

        return concave_gdf,totalarea

    else:
        no_results='the search did not work'
        return no_results
    
def divider(factorlist,divideby,maxwidth,maxheight):        
    
    ### IF REALLY TALL just divide height up
    
    if maxwidth/maxheight <= 0.125:
        print('<0.125')
        height = maxheight/divideby
        width = maxwidth

    ### IF pretty tall increase the factorlist
    
    elif maxwidth/maxheight <0.33:
        print('<0.33')
        while len(factorlist)==2:
            factorlist=[]
            for i in range(1, divideby+2):
                #print(f'i is {i}')
                divide=divideby+1
                if divide%i==0:
                    print(f'divideby+1 is {divideby+1}')
                    print((divideby)%i)
                    factorlist.append(i)
            divideby=divide
            
        else:
            factorsplit=[]
            factorsplit.append(factorlist[1])
            factorsplit.append(factorlist[-2])

        height=maxheight/factorsplit[1]
        width=maxwidth/factorsplit[0]

    elif maxwidth/maxheight <=1:
        print('<1')
        print(len(factorlist))
        while len(factorlist)<=4:
            factorlist=[]
            for i in range(1, divideby+2):
                #print(f'i is {i}')
                divide=divideby+1
                if divide%i==0:
                    print(f'divideby+1 is {divideby+1}')
                    print((divideby)%i)
                    factorlist.append(i)
            divideby=divide
        if len(factorlist)==6:
            factorsplit=[]
            factorsplit.append(factorlist[2])
            factorsplit.append(factorlist[3])

        elif len(factorlist)==8:
            factorsplit=[]
            factorsplit.append(factorlist[3])
            factorsplit.append(factorlist[4])
        elif len(factorlist)==10:
            factorsplit=[]
            factorsplit.append(factorlist[4])
            factorsplit.append(factorlist[5])
            
        else:
            factorsplit=[]
            factorsplit.append(factorlist[1])
            factorsplit.append(factorlist[-2])

        height=maxheight/factorsplit[1]
        width=maxwidth/factorsplit[0]
        

    elif maxwidth/maxheight <2:
        print('<2')
        while len(factorlist)<=3:
            factorlist=[]
            for i in range(1, divideby+2):
                #print(f'i is {i}')
                divide=divideby+1
                if divide%i==0:
                    print(f'divideby+1 is {divideby+1}')
                    print((divideby)%i)
                    factorlist.append(i)
            divideby=divide
        if len(factorlist)==6:
            factorsplit=[]
            factorsplit.append(factorlist[3])
            factorsplit.append(factorlist[2])

        elif len(factorlist)==8:
            factorsplit=[]
            factorsplit.append(factorlist[3])
            factorsplit.append(factorlist[4])
        elif len(factorlist)==10:
            factorsplit=[]
            factorsplit.append(factorlist[4])
            factorsplit.append(factorlist[5])
        elif len(factorlist)==12:
            factorsplit=[]
            factorsplit.append(factorlist[5])
            factorsplit.append(factorlist[6])
            
            
        else:
            factorsplit=[]
            factorsplit.append(factorlist[1])
            factorsplit.append(factorlist[-2])


        height=maxheight/factorsplit[0]
        width=maxwidth/factorsplit[1]


    elif maxwidth/maxheight <6:
        print('<6')
        print(factorlist)
        while len(factorlist)==2:
            factorlist=[]
            for i in range(1, divideby+2):
                #print(f'i is {i}')
                divide=divideby+1
                if divide%i==0:
                    print(f'divideby+1 is {divideby+1}')
                    print((divideby)%i)
                    factorlist.append(i)
            divideby=divide
        if len(factorlist)==4:
            print(f'factorlist4 {factorlist}')
            factorsplit=[]
            factorsplit.append(factorlist[2])
            factorsplit.append(factorlist[1])
            print(factorsplit)

        elif len(factorlist)==6:
            print('factorlist6')
            factorsplit=[]
            factorsplit.append(factorlist[3])
            factorsplit.append(factorlist[2])
            
        else:
            factorsplit=[]
            factorsplit.append(factorlist[1])
            factorsplit.append(factorlist[-1])

        print(factorsplit) # 4,3
        height=maxheight/factorsplit[1]
        print(height)
        width=maxwidth/factorsplit[0]
        print(width)

    #elif maxwidth/maxheight <= 12:
    else:
        print(divideby)
        height = maxheight
        width = maxwidth/(divideby)
        
    return [width,height]

def EAPGrid_new(gdf,max_area):
    
    #Check the area of the input and if it's >600 split it.
       
    
    
    #Iterate through gdf 
    
    outgdf=gpd.GeoDataFrame()
    for cur_row in range(len(gdf)):
        cur_row_gdf=gdf.iloc[[cur_row]]
        cur_row_area=aoi_areakm(cur_row_gdf,'area')
        cur_row_area=cur_row_area.reset_index(drop=True)
        if cur_row_area['area'][0] > max_area:
            print(f'cur row area is {cur_row_area["area"][0]},{max_area}')
        #Create Centroid for projection - this assumes that the index of the item is 0 and there is only 1 AOI polygon is being added OR it is being passed a new iloc gdf.
            if cur_row_gdf.geom_type[cur_row] in ['Point','Polygon', 'MultiPolygon']:
                pol2=gdf.centroid[cur_row]
                print(gdf.centroid[cur_row])
                pass
            else:
                print("not valid geometry")

            #print(pol2)
            wgs84_globe = pyproj.Proj(proj='longlat', ellps='WGS84')

            aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=pol2.y, lon_0=pol2.x)

            projpol = sh_transform(partial(pyproj.transform, wgs84_globe, aeqd), cur_row_gdf['geometry'][cur_row]) 
            print(projpol)
            temp=gpd.GeoSeries(projpol)
            boundary=temp.bounds

            # get length of bounding box edges
            edge_width = (Point(boundary['minx'][0],boundary['miny'][0])).distance(Point(boundary['maxx'][0],boundary['miny'][0]))
            edge_height =(Point(boundary['minx'][0],boundary['miny'][0])).distance(Point(boundary['minx'][0],boundary['maxy'][0]))

            print(f'max width is = {edge_width}, max height is = {edge_height}')

            poly_geometry = [
                        (boundary['minx'][0], boundary['miny'][0]),
                        (boundary['minx'][0], boundary['maxy'][0]),
                        (boundary['maxx'][0], boundary['maxy'][0]),
                        (boundary['maxx'][0], boundary['miny'][0]),
                        (boundary['minx'][0], boundary['miny'][0]),
                        ]



            newppp=(sh_transform(partial(pyproj.transform, aeqd, wgs84_globe), Polygon(poly_geometry)))
            print(newppp)
            #poly_geometry=Polygon(newppp)
            #print(poly_geometry)
            gs=gpd.GeoSeries(newppp)
            polygdf=gpd.GeoDataFrame(geometry=gs)
            #print(polygdf.crs)
            polygdf=aoi_areakm(deepcopy(polygdf),'area')
            gdf_area=aoi_areakm(deepcopy(gdf),'area')
            gdf_area=gdf_area.reset_index(drop=True)
            area=gdf_area['area'][0]
            bbarea=polygdf['area'][0]



            print(f'bounding area = {bbarea}')

            divideby=int(math.ceil(bbarea/max_area)) 

            print(f'divideby is {divideby}')

            boundsarea=bbarea/divideby
            area=boundsarea*1000000
            print(area)

            minwidth = 1000
            maxwidth=edge_width
            maxheight=edge_height

            #print(f'area is {area}')
            print(f'maxwidth is {maxwidth}')


            val_range = range(0,100)




            factorlist=[]
            if divideby >3:
                #Add if maxwidth/maxheight factor for option of single row
                print('divide by >3')
                for i in range(1, divideby+1):
                    if divideby % i == 0:
                        factorlist.append(i)
                print(factorlist)
                division=divider(factorlist,divideby,maxwidth,maxheight)        
                width=division[0]
                height=division[1]



                # Python Program to find the factors of a number
            elif divideby<4 or maxwidth/maxheight <=0.5 or maxwidth/maxheight >=5:
                print('divideby <4 or high ratio')
                if maxwidth/maxheight <=1:
                    height = maxheight/divideby
                    width = maxwidth
                elif maxwidth/maxheight >1:
                    height=maxheight
                    width=maxwidth/divideby
                    print(f'width is {width}')
    #Edited to remove branching logic
            #else: #divideby <= 12:
                #print('divideby <= 12')
                else:

                    division=divider(factorlist,divideby,maxwidth,maxheight)        
                    width=division[0]
                    height=division[1]



            cols = list(np.arange(boundary['minx'][0], boundary['maxx'][0]+int(math.ceil(width)), int(math.ceil(width))))
            print(cols)
            rows = list(np.arange(boundary['miny'][0], boundary['maxy'][0]+int(math.ceil(height)), int(math.ceil(height))))
            print(rows)
            polyproj=[]
            for x in cols[:-1]:
                #print(x)
                for y in rows[:-1]:
                    #print(y)
                    newpoly=(Polygon([(x,y), (x+width, y), (x+width, y+height), (x, y+height)]))
                    newpolypro=(sh_transform(partial(pyproj.transform, aeqd, wgs84_globe), newpoly))
                    polyproj.append(newpolypro)  

            gdfname=gpd.GeoDataFrame(geometry=polyproj)
            gdfname=aoi_areakm(deepcopy(gdfname),'area')
            #Totalarea = gdfname['area'].sum()
            #print(Totalarea)
            print(f'gdf name is length {len(gdfname)}')
            #print(type(gdfname))  
            #if len(gdfname)==divideby:
                #if Totalarea < area:
            

            gridoverlap=EAProject_Buffer(gdfname,5,3)
            intersectgs=gridoverlap.intersection(cur_row_gdf['geometry'][cur_row])
            intersectgdf=gpd.GeoDataFrame(geometry=intersectgs)
            intersectgdf=intersectgdf.explode()
            intersectgdf=intersectgdf.reset_index(drop=True)
            intersectgdf = intersectgdf[intersectgdf.is_empty != True]
            combgdf=combine_geom(intersectgdf)
            
            outgdf=outgdf.append(combgdf)
            print(type(outgdf))


    return outgdf
    #return polyGS
    
def combine_geom(intersectgdf,max_area):
    newgdf=deepcopy(intersectgdf)
 
    newgdf=newgdf.explode()
    newgdf=newgdf.reset_index(drop=True)
    newgdf=newgdf[~newgdf.is_empty]
    #print(newgdf.index)
    newgdflist=[]
    #maxindex=max(newgdf.index)
    count=0
    area_variable1=5
    area_variable2=max_area-5
    for num in range(0,11):
        print(f'run {num}')
        if num <=4:
            area_variable1=area_variable1+1
            area_variable2=area_variable2
        elif num <=6:
            area_variable1=area_variable1+2
            area_variable2=area_variable2-5
        else:
            area_variable1=area_variable1+5
            area_variable2=area_variable2-5

        #calculate area
        newgdf=aoi_areakm(newgdf,'area')
        #sort by area
        newgdf=newgdf.sort_values('area', axis=0, ascending=True)
        #reset index§§§§

        newgdf=newgdf.reset_index(drop=True)
        maxindex=max(newgdf.index)
        polygdf=gpd.GeoDataFrame(columns=['geometry'])

            #iterate through the gdf
        for row in newgdf.itertuples():
            gdf_index1=getattr(row,"Index")
            if gdf_index1 not in newgdf.index:
                print('nothing with that index')
                pass
            else:

                if getattr(row,'area')<=area_variable1:

                    polygon=getattr(row,'geometry')

                    polarea=getattr(row,'area')
                    print(f'first area is {polarea}')
                    #polylist.append(polygon)
                    #iterate through the gdf a second time to compare rows
                    for row2 in newgdf.itertuples():
                        gdf_index2=getattr(row2,"Index")
                        if gdf_index2 not in newgdf.index:
                            #print('nothing with that index2')
                            pass
                        else:

                            polarea2=getattr(row2,'area')
                            polygon2=getattr(row2,'geometry')
                            #print(f'second area is {polarea2}')
                            item=polygon2.intersects(polygon)
                            overlap=(polygon.intersection(polygon2).area/polygon.area)*100
                            print(overlap)
                            #if the polygons do not match and they have overlap, then move on.

                            if polygon != polygon2 and polarea2 >= area_variable2 and item == True and (polarea+polarea2)<=50 and overlap > 0.02:
                                print('lets try to merge!')
                                polygons=[polygon,polygon2]
                                boundary = gpd.GeoSeries(shapely.ops.unary_union(polygons))
                                maxindex=maxindex+1
                                boundary2=gpd.GeoDataFrame(geometry=boundary)
                                boundary2=boundary2.set_index([[maxindex]])


                                #print(sum([(cur_row_gdf['area'][cur_row_gdf.index[0]]), (prev_row_gdf['area'][prev_row_gdf.index[0]])]))
                                merge_area=aoi_areakm(boundary2,'area')
                                #print(f'the area is {merge_area.area[maxindex]}')
                                #merge_area=merge_area.reset_index(drop=True)
                                mergy=merge_area.is_valid
                                if mergy[maxindex] == True:
                                    #print(merge_area['area'])
                                    newgdf=newgdf.drop(gdf_index1)
                                    newgdf=newgdf.drop(gdf_index2)
                                    newgdf=newgdf.append(merge_area)

                                    print('sum is less than 50')
                                    geoframe=range(len(newgdf))
                                    break
                                else:
                                    pass
                                
    return newgdf
