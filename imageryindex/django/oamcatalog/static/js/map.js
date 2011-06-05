OpenLayers.Util.onImageLoadError = function () {} ;
var OAMFormat = OpenLayers.Class(OpenLayers.Format.JSON, {
    'read': function(json,filter) {
        if (typeof json == "string") {
            obj = OpenLayers.Format.JSON.prototype.read.apply(this,
                                                              [json, filter]);
        } else { 
            obj = json;
        }    
        if(!obj) {
            OpenLayers.Console.error("Bad JSON: " + json);
        }
        var features = [];
        for (i = 0; i < obj.images.length; i++) {
            var image = obj.images[i];
            var bounds = OpenLayers.Bounds.fromArray(image.bbox);
            var f = new OpenLayers.Feature.Vector(bounds.toGeometry());
            f.image = image;
            features.push(f);
        }
        return features;
    }
});

var map, selectControl, selectedFeature;
function onPopupClose(evt) {
    selectControl.unselect(selectedFeature);
    evt.stopPropagation()
}

function onFeatureSelect(feature) {
    selectedFeature = feature;
    popup = new OpenLayers.Popup.FramedCloud("chicken",
                                 feature.geometry.getBounds().getCenterLonLat(),
                                 null,
                                 '<div><a href="/image/' + feature.image.id + '">Image ' + feature.image.id + '</a></div>',
                                 null, true, onPopupClose);
    feature.popup = popup;
    map.addPopup(popup);
}

function onFeatureUnselect(feature) {
    map.removePopup(feature.popup);
    feature.popup.destroy();
    feature.popup = null;
    selectedFeature = null;
}
        
function createMap(url, div){
    map = new OpenLayers.Map( 'map', {displayProjection: new OpenLayers.Projection("EPSG:4326")} );
    var layer = new OpenLayers.Layer.OSM("OSM");
    map.addLayer(layer);
    layer = new OpenLayers.Layer.Vector("", {
        strategies: [new OpenLayers.Strategy.BBOX({resFactor: 1.1,ratio:1.0})],
        protocol: new OpenLayers.Protocol.HTTP({
           url: url,
           format: new OAMFormat()
        }),
         styleMap: new OpenLayers.StyleMap({'strokeColor': '#000000', 'strokeWidth': 2, fillOpacity: 0}),
        'renderers': ['Canvas', 'VML']
        });
    map.addLayer(layer); 
    layer.events.register("loadend", layer, function() {
        if (map.getCenter().lat == 0 && map.getCenter().lon == 0) {
          layer.map.zoomToExtent(layer.getDataExtent());
        }  
    });   
//    map.addControl(new OpenLayers.Control.Permalink());
    selectControl = new OpenLayers.Control.SelectFeature(layer,
        {onSelect: onFeatureSelect, onUnselect: onFeatureUnselect});
    map.addControl(selectControl);
    selectControl.activate();
    
    if (!map.getCenter()) {
        map.zoomToMaxExtent();
    } else {
        // kick the bbox strategy
        map.setCenter();
    }    
}

