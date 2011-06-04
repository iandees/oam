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
            features.push(f);
        }
        return features;
    }
});
        
function createMap(url, div){
    var map = new OpenLayers.Map( 'map', {displayProjection: new OpenLayers.Projection("EPSG:4326")} );
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
    
    if (!map.getCenter()) {
        map.zoomToMaxExtent();
    } else {
        // kick the bbox strategy
        map.setCenter();
    }    
}

