var map;
var json;
var infoWindow;
var allPolylines = [];
var bounds;
var searchArea;
var searchablePlants;
var otherPlants = [];
var bigPlantData = [];
var currentView;
var intersectOutline;
var position;

async function initMap() {
  var mapDiv = document.getElementById('map-google');
  var styledMapType = new google.maps.StyledMapType(
      [
        {
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#ebe3cd"
            }
          ]
        },
        {
          "elementType": "labels.text.fill",
          "stylers": [
            {
              "color": "#523735"
            }
          ]
        },
        {
          "elementType": "labels.text.stroke",
          "stylers": [
            {
              "color": "#f5f1e6"
            }
          ]
        },
        {
          "featureType": "administrative",
          "elementType": "geometry.stroke",
          "stylers": [
            {
              "color": "#c9b2a6"
            }
          ]
        },
        {
          "featureType": "landscape.man_made",
          "elementType": "labels",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "landscape.man_made",
          "elementType": "labels.icon",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "landscape.natural",
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#dfd2ae"
            }
          ]
        },
        {
          "featureType": "landscape.natural.terrain",
          "stylers": [
            {
              "visibility": "on"
            }
          ]
        },
        {
          "featureType": "landscape.natural.terrain",
          "elementType": "geometry",
          "stylers": [
            {
              "visibility": "on"
            }
          ]
        },
        {
          "featureType": "landscape.natural.terrain",
          "elementType": "geometry.fill",
          "stylers": [
            {
              "visibility": "on"
            }
          ]
        },
        {
          "featureType": "landscape.natural.terrain",
          "elementType": "geometry.stroke",
          "stylers": [
            {
              "visibility": "on"
            }
          ]
        },
        {
          "featureType": "poi",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "poi",
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#dfd2ae"
            }
          ]
        },
        {
          "featureType": "poi",
          "elementType": "labels.text",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "poi",
          "elementType": "labels.text.fill",
          "stylers": [
            {
              "color": "#93817c"
            }
          ]
        },
        {
          "featureType": "poi.park",
          "stylers": [
            {
              "visibility": "on"
            }
          ]
        },
        {
          "featureType": "poi.park",
          "elementType": "geometry.fill",
          "stylers": [
            {
              "color": "#a5b076"
            }
          ]
        },
        {
          "featureType": "poi.park",
          "elementType": "labels.text.fill",
          "stylers": [
            {
              "color": "#005f00"
            }
          ]
        },
        {
          "featureType": "road",
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#f5f1e6"
            }
          ]
        },
        {
          "featureType": "road",
          "elementType": "labels.icon",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "road.arterial",
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#fdfcf8"
            }
          ]
        },
        {
          "featureType": "road.arterial",
          "elementType": "labels",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "road.highway",
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#f8c967"
            }
          ]
        },
        {
          "featureType": "road.highway",
          "elementType": "geometry.stroke",
          "stylers": [
            {
              "color": "#e9bc62"
            }
          ]
        },
        {
          "featureType": "road.highway",
          "elementType": "labels",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "road.highway.controlled_access",
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#e98d58"
            }
          ]
        },
        {
          "featureType": "road.highway.controlled_access",
          "elementType": "geometry.stroke",
          "stylers": [
            {
              "color": "#db8555"
            }
          ]
        },
        {
          "featureType": "road.local",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "road.local",
          "elementType": "labels.text.fill",
          "stylers": [
            {
              "color": "#806b63"
            }
          ]
        },
        {
          "featureType": "transit",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "transit.line",
          "stylers": [
            {
              "visibility": "on"
            }
          ]
        },
        {
          "featureType": "transit.line",
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#dfd2ae"
            },
            {
              "visibility": "on"
            }
          ]
        },
        {
          "featureType": "transit.line",
          "elementType": "labels.text.fill",
          "stylers": [
            {
              "color": "#8f7d77"
            }
          ]
        },
        {
          "featureType": "transit.line",
          "elementType": "labels.text.stroke",
          "stylers": [
            {
              "color": "#ebe3cd"
            }
          ]
        },
        {
          "featureType": "transit.station",
          "stylers": [
            {
              "visibility": "simplified"
            }
          ]
        },
        {
          "featureType": "transit.station",
          "elementType": "geometry",
          "stylers": [
            {
              "color": "#dfd2ae"
            }
          ]
        },
        {
          "featureType": "water",
          "elementType": "geometry.fill",
          "stylers": [
            {
              "color": "#b9d3c2"
            }
          ]
        },
        {
          "featureType": "water",
          "elementType": "labels.text.fill",
          "stylers": [
            {
              "color": "#92998d"
            }
          ]
        }
      ],
          {name: 'Huckleberry'});
  map = await new google.maps.Map(mapDiv, {
      center: {
          lat: 37.815962882132034,
          lng: -122.30391338701173
      },
      zoom: 12,
      fullscreenControl: false,
      streetViewControl: false,
      mapTypeControl: true,
      mapTypeControlOptions: {
          mapTypeIds: ['roadmap', 'satellite', 'hybrid', 'terrain',
                  'styled_map'],
          // style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
          position: google.maps.ControlPosition.BOTTOM_CENTER
                }
  });
  map.mapTypes.set('styled_map', styledMapType);
  map.setMapTypeId('styled_map');
  // ['zoom_changed','center_changed'].forEach( function(evt) {
  //   map.addListener(evt, function() {getPlants()}, false);
  //   });
  google.maps.event.addListenerOnce(map, 'idle', function(){getPlants()});

  // map.addListener('bounds_changed', function() {getPlants()});
  
  setTimeout(() => {
    $(".main").fadeIn();
    $(".loading-page").fadeOut("slow", () => {
      $(".loading-page").remove()
    })
  }, 5000);
  // debugger
  // searchArea = map.getBounds().toJSON();//bounds
  $("#multiCollapseExample1").load('/templates/plant-to-hike.html', addTheButton);
  $('#exampleModalCenter').on('show.bs.modal', editModal)
};

/////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.get("/popover", function (data) {
      $("#cover-video").attr("src", data);
      // console.log(data)
    })
});
    
/////////////////////////////////////////////////////////////////////////////


function addTheButton() {
    $("#multiCollapseExample1 .input-group-append .btn").click(function () {
        addByPlantSearch( $("#multiCollapseExample1 .typeahead").val() );
    $("#multiCollapseExample1 .typeahead").val("");
      });
}
/////////////////////////////////////////////////////////////////////////////

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

/////////////////////////////////////////////////////////////////////////////

$(document).click(function(e) {
  if ($(e.target).is('.glass-blur')) {
      $('.collapse').collapse('hide');      
    }
});

/////////////////////////////////////////////////////////////////////////////


async function loadTrails(jsonTrails){

  for (var trail in jsonTrails){
    let trailPath = new google.maps.Polyline({
        path: jsonTrails[trail]["path"],
        geodesic: true,
        strokeColor: '#b50909',
        strokeOpacity: 0.25,
        strokeWeight: 2,
        jointType: 2,
        clickable: true
          });

    if (!allPolylines.includes(trailPath)) {
      allPolylines.push(trailPath);

      trailPath.setMap(map);
      infoWindow = new google.maps.InfoWindow();
      trailPath.html = jsonTrails[trail]["name"];

      google.maps.event.addListener(trailPath, 'mouseover', function(e) {
         infoWindow.setPosition(e.latLng);
         infoWindow.setContent(this.html);
         infoWindow.open(map, this);
         //for future decelopment, I'd like to also have the trailhead appear and disappear as you mouseover
         });

      // Close the InfoWindow on mouseout:
      google.maps.event.addListener(trailPath, 'mouseout', function() {
         infoWindow.close();
         });
      }
    }

  };

/////////////////////////////////////////////////////////////////////////////


function getPlants() {
  console.log("lol running getPlants again")
  mapBounds = map.getBounds().toJSON();
  let toSend = {
    mapBoundary: mapBounds, //check if it wants the current view only or all of CA
    andOr: "and", //hardcoded for now
    intersectingPlants: otherPlants
  };
  // console.log(mapBounds)

  $.ajax({
    url: '/get-plants.json',
    dataType: 'json',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(toSend),
    processData: false,
    success: function(data, textStatus, jQxhr ){
        console.log("received data, trying to do intersection stuff");
        console.log(data)
        plantIntersect(data);
        },
    error: function() {
      alert("No plants were returned.")
    }
  });
};

/////////////////////////////////////////////////////////////////////////////

async function plantIntersect(plantIntersectionData){
  bounds = {
    north: plantIntersectionData["new_bounds"]["north"],
    south: plantIntersectionData["new_bounds"]["south"],
    east: plantIntersectionData["new_bounds"]["east"],
    west: plantIntersectionData["new_bounds"]["west"]
  };
  // bounds = new google.maps.LatLngBounds();
  // var neCorner = new google.maps.LatLng(plantIntersectionData["new_bounds"]["north"], plantIntersectionData["new_bounds"]["east"]);//(N, E)
  // var swCorner = new google.maps.LatLng(plantIntersectionData["new_bounds"]["south"], plantIntersectionData["new_bounds"]["west"]);;
  // bounds.extend(neCorner);
  // bounds.extend(swCorner);

  // map.fitBounds(bounds); // <- this is too dangerous

  searchablePlants = plantIntersectionData["visible_plants"];
  $("#query").typeahead({ source:searchablePlants });


  for (line of allPolylines){
    line.setMap(null);
    line = null
  };

  allPolylines = [];
  
  drawIntersection(plantIntersectionData["intersection"]);
  loadTrails(plantIntersectionData["visible_trails"])
};

/////////////////////////////////////////////////////////////////////////////

async function drawIntersection(intersectionPoints){
    if (typeof intersectOutline !== 'undefined') {
      intersectOutline.setMap(null);
      intersectOutline = null
    } else {};


    intersectOutline = new google.maps.Polygon({
      paths: intersectionPoints,
      strokeColor: '#FFFFFF',
      strokeOpacity: 0.1,
      strokeWeight: 2,
      fillColor: '#FFFFFF',
      fillOpacity: 0.1
    });

    intersectOutline.setMap(map);
    if (otherPlants.length != 0) {pulseOutline(intersectOutline)};
    
    console.log("printed the intersecton")
  }

/////////////////////////////////////////////////////////////////////////////

function pulseOutline(intersectOutline) {
  var currentFill = 0.11;
  var currentIncrement = +0.01
  setInterval(function() {
    intersectOutline.setOptions({strokeOpacity: currentFill, fillOpacity: currentFill});
    if (currentFill>=0.75 || currentFill<=0.01){
      currentIncrement = (-1)*currentIncrement
    };
    currentFill += currentIncrement;
    // console.log(currentFill)
  }, 75);
}

// function componentToHex(c) {
//   var hex = c.toString(16);
//   return hex.length == 1 ? "0" + hex : hex;
// }

// function rgbToHex(r, g, b) {
//   return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
// }
/////////////////////////////////////////////////////////////////////////////

function addByPlantSearch(plantName){
  console.log("I did a thing")
  console.log(plantName)
  // ask the db for the id of the plant from its name
  // get the metadata for that plant 
  // check if it's already in otherPlants
  // if not, 
        // add it to otherPlants
        // add a card about it to the side that stores all the information so it can be passed to Modal
  $.ajax({
      url: '/get-plant-data.json',
      dataType: 'json',
      type: 'POST',
      contentType: 'text/html; charset=utf-8',
      data: plantName,
      processData: false,
      success: function(data, textStatus, jQxhr ){
        console.log(data);
        console.log("hi");
        addToCards(data)
        getPlants();
          },
      error: function() {
        alert("No plants of that name were found.")
      }
    });
  };

/////////////////////////////////////////////////////////////////////////////

async function addToCards(plantData, otherPlants) {
  if (!window.otherPlants.includes(plantData["plant_id"])) {
    // add it to otherPlants
    window.otherPlants.push(plantData["plant_id"]);
    window.bigPlantData.push(plantData);
    await getPlants();
    // add a card about it to the side that stores all the information so it can be passed to Modal 
    $("#multiCollapseExample1 > .card > .result-row")[0].insertAdjacentHTML('afterend', plantData["card_html"]);
    for (i of $("#multiCollapseExample1 > div > div > div.col > button")) {
      $(i).click(function() {
        var delID = $($(this).parent().siblings(".card .bg-light")[0]).data("plant-id");
        console.log(delID);
        position = $.inArray(delID, otherPlants);
        console.log(position);
        console.log((position < 0));
        console.log("doin it")
        fixIndex()

        $(this).parent().parent().remove()
        getPlants()
        //remove from other_plants and run getPlants again

        })
      } 
  }};

function fixIndex(){
  if (position <= 0) {
          position = otherPlants.length + position
        };
  console.log(position);
  if ( ~position ) otherPlants.splice(position, 1) //delete that ID from 'otherPlants'
}
/////////////////////////////////////////////////////////////////////////////

function editModal(event) {
  console.log("modal is showing");
  var plantRow = $(event.relatedTarget);// row that triggered the modal
  // Extract info from data-* attributes
  console.log(plantRow);
  console.log(plantRow.data('alt-names'))

  var sciName = plantRow.data('sci-name');
  if (plantRow.data('alt-names') != "none"){
    var altNames = eval(plantRow.data('alt-names'))
  } else {var altNames = plantRow.data('alt-names')};
  // var altNames = eval(plantRow.data('alt-names'));

  var plantType = plantRow.data('plant-type');
  if (plantRow.data('plant-shape') != "none"){
    var plantShape = eval(plantRow.data('plant-shape'))//.replace("!", "'").replace(",", ", ")
  } else {var plantShape = plantRow.data('plant-shape')};
  // var plantShape = eval(plantRow.data('plant-shape'));

  
  var minHeight = plantRow.data('min-height');
  var maxHeight = plantRow.data('max-height');
  if (minHeight!="none" && maxHeight!="none"){
      var plantHeight = minHeight+"-"+maxHeight+" ft.";
  } else if (minHeight=="none" && maxHeight!="none") {
    var plantHeight = "Up to "+maxHeight+" ft.";
  } else if (minHeight!="none" && maxHeight=="none") {
    var plantHeight = "Over "+minHeight+" ft.";
  } else if (minHeight=="none" && maxHeight=="none") {
    var plantHeight = "Unknown"
  };


  var tox = plantRow.data('toxicity-notes');
  var rare = plantRow.data('rare');
  var bloomBegin = plantRow.data('bloom-begin');
  var bloomEnd = plantRow.data('bloom-end');
  if (plantRow.data('flower-color') != "none"){
    var flowerCol = eval(plantRow.data('flower-color'))
  } else {var flowerCol = "None"};
  // var flowerCol = plantRow.data('flower-color');

  var desc = plantRow.data('verbose-desc').replace("!", "'");

  if (plantRow.data('photo-options') != "none"){
    var photoOptions = eval(plantRow.data('photo-options'))
  } else {var photoOptions = plantRow.data('photo-options')};
  // var photoOptions = eval(plantRow.data('photo-options'));

  var calphotosUrl = plantRow.data('calphotos-url');
  var characteristicsUrl = plantRow.data('characteristics-url');
  var jepsonUrl = plantRow.data('jepson-url');
  var calscapeUrl = plantRow.data('calscape-url');
  var usdaPlantsUrl = plantRow.data('usda-plants-url');
  var cnpsRareUrl = plantRow.data('cnps-rare-url');

  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  var modal = $(this);

  for (item of modal.find(".carousel-item")) {
    if (!$(item).hasClass("original-carousel")) {
      item.remove()
    }};
  // for (item of modal.find(".carousel-item")){
  //   item.remove()
  // };

  for (photo of photoOptions) {
    modal.find(".carousel-item")[0].insertAdjacentHTML("afterend", "<div class='carousel-item'><img class='d-block img-thumbnail' src='"+photo+"' alt='First slide' style='display:block;margin-left:auto;margin-right:auto;width:8em;height:8em;'></div>")
  };

  modal.find(".original-carousel")[0].remove();
  $(modal.find(".carousel-item")[0]).addClass('active');
  $(modal.find(".carousel-item")[0]).addClass('original-carousel');

  modal.find('.modal-title').text(altNames[0].replace("!", "'"));
  modal.find('.modal-body #sci-name').text(sciName);
  modal.find('.modal-body #alt-names').text(altNames);
  modal.find('.modal-body #type').text(plantType);
  modal.find('.modal-body #shape').text(plantShape);
  modal.find('.modal-body #height').text(plantHeight);
  modal.find('.modal-body #toxicity').text(tox);
  modal.find('.modal-body #rarity').text(rare);
  modal.find('.modal-body #blooming').text(bloomBegin);
  modal.find('.modal-body #flower-color').text(flowerCol);
  modal.find('.modal-body #description').text(desc);


  modal.find('.modal-body #alt-names').text(modal.find('.modal-body #alt-names').text().replace(",", ", "));
  modal.find('.modal-body #type').text(modal.find('.modal-body #type').text().replace(",", ", "));
  modal.find('.modal-body #shape').text(modal.find('.modal-body #shape').text().replace(",", ", "));
  modal.find('.modal-body #flower-color').text(modal.find('.modal-body #flower-color').text().replace(",", ", "));
  modal.find('.modal-body #alt-names').text(modal.find('.modal-body #alt-names').text().replace("!", "'"));
  modal.find('.modal-body #type').text(modal.find('.modal-body #type').text().replace("!", "'"));
  modal.find('.modal-body #shape').text(modal.find('.modal-body #shape').text().replace("!", "'"));
  modal.find('.modal-body #flower-color').text(modal.find('.modal-body #flower-color').text().replace("!", "'"));
}


/////////////////////////////////////////////////////////////////////////////



//https://github.com/bassjobsen/Bootstrap-3-Typeahead
!function(root,factory){"use strict";"undefined"!=typeof module&&module.exports?module.exports=factory(require("jquery")):"function"==typeof define&&define.amd?define(["jquery"],function($){return factory($)}):factory(root.jQuery)}(this,function($){"use strict";var Typeahead=function(element,options){this.$element=$(element),this.options=$.extend({},Typeahead.defaults,options),this.matcher=this.options.matcher||this.matcher,this.sorter=this.options.sorter||this.sorter,this.select=this.options.select||this.select,this.autoSelect="boolean"!=typeof this.options.autoSelect||this.options.autoSelect,this.highlighter=this.options.highlighter||this.highlighter,this.render=this.options.render||this.render,this.updater=this.options.updater||this.updater,this.displayText=this.options.displayText||this.displayText,this.itemLink=this.options.itemLink||this.itemLink,this.itemTitle=this.options.itemTitle||this.itemTitle,this.followLinkOnSelect=this.options.followLinkOnSelect||this.followLinkOnSelect,this.source=this.options.source,this.delay=this.options.delay,this.theme=this.options.theme&&this.options.themes&&this.options.themes[this.options.theme]||Typeahead.defaults.themes[Typeahead.defaults.theme],this.$menu=$(this.options.menu||this.theme.menu),this.$appendTo=this.options.appendTo?$(this.options.appendTo):null,this.fitToElement="boolean"==typeof this.options.fitToElement&&this.options.fitToElement,this.shown=!1,this.listen(),this.showHintOnFocus=("boolean"==typeof this.options.showHintOnFocus||"all"===this.options.showHintOnFocus)&&this.options.showHintOnFocus,this.afterSelect=this.options.afterSelect,this.afterEmptySelect=this.options.afterEmptySelect,this.addItem=!1,this.value=this.$element.val()||this.$element.text(),this.keyPressed=!1,this.focused=this.$element.is(":focus")};Typeahead.prototype={constructor:Typeahead,setDefault:function(val){if(this.$element.data("active",val),this.autoSelect||val){var newVal=this.updater(val);newVal||(newVal=""),this.$element.val(this.displayText(newVal)||newVal).text(this.displayText(newVal)||newVal).change(),this.afterSelect(newVal)}return this.hide()},select:function(){var val=this.$menu.find(".active").data("value");if(this.$element.data("active",val),this.autoSelect||val){var newVal=this.updater(val);newVal||(newVal=""),this.$element.val(this.displayText(newVal)||newVal).text(this.displayText(newVal)||newVal).change(),this.afterSelect(newVal),this.followLinkOnSelect&&this.itemLink(val)?(document.location=this.itemLink(val),this.afterSelect(newVal)):this.followLinkOnSelect&&!this.itemLink(val)?this.afterEmptySelect(newVal):this.afterSelect(newVal)}else this.afterEmptySelect(newVal);return this.hide()},updater:function(item){return item},setSource:function(source){this.source=source},show:function(){var element,pos=$.extend({},this.$element.position(),{height:this.$element[0].offsetHeight}),scrollHeight="function"==typeof this.options.scrollHeight?this.options.scrollHeight.call():this.options.scrollHeight;if(this.shown?element=this.$menu:this.$appendTo?(element=this.$menu.appendTo(this.$appendTo),this.hasSameParent=this.$appendTo.is(this.$element.parent())):(element=this.$menu.insertAfter(this.$element),this.hasSameParent=!0),!this.hasSameParent){element.css("position","fixed");var offset=this.$element.offset();pos.top=offset.top,pos.left=offset.left}var newTop=$(element).parent().hasClass("dropup")?"auto":pos.top+pos.height+scrollHeight,newLeft=$(element).hasClass("dropdown-menu-right")?"auto":pos.left;return element.css({top:newTop,left:newLeft}).show(),!0===this.options.fitToElement&&element.css("width",this.$element.outerWidth()+"px"),this.shown=!0,this},hide:function(){return this.$menu.hide(),this.shown=!1,this},lookup:function(query){if(this.query=void 0!==query&&null!==query?query:this.$element.val(),this.query.length<this.options.minLength&&!this.options.showHintOnFocus)return this.shown?this.hide():this;var worker=$.proxy(function(){$.isFunction(this.source)&&3===this.source.length?this.source(this.query,$.proxy(this.process,this),$.proxy(this.process,this)):$.isFunction(this.source)?this.source(this.query,$.proxy(this.process,this)):this.source&&this.process(this.source)},this);clearTimeout(this.lookupWorker),this.lookupWorker=setTimeout(worker,this.delay)},process:function(items){var that=this;return items=$.grep(items,function(item){return that.matcher(item)}),(items=this.sorter(items)).length||this.options.addItem?(items.length>0?this.$element.data("active",items[0]):this.$element.data("active",null),"all"!=this.options.items&&(items=items.slice(0,this.options.items)),this.options.addItem&&items.push(this.options.addItem),this.render(items).show()):this.shown?this.hide():this},matcher:function(item){return~this.displayText(item).toLowerCase().indexOf(this.query.toLowerCase())},sorter:function(items){for(var item,beginswith=[],caseSensitive=[],caseInsensitive=[];item=items.shift();){var it=this.displayText(item);it.toLowerCase().indexOf(this.query.toLowerCase())?~it.indexOf(this.query)?caseSensitive.push(item):caseInsensitive.push(item):beginswith.push(item)}return beginswith.concat(caseSensitive,caseInsensitive)},highlighter:function(item){var text=this.query;if(""===text)return item;var i,matches=item.match(/(>)([^<]*)(<)/g),first=[],second=[];if(matches&&matches.length)for(i=0;i<matches.length;++i)matches[i].length>2&&first.push(matches[i]);else(first=[]).push(item);text=text.replace(/[\(\)\/\.\*\+\?\[\]]/g,function(mat){return"\\"+mat});var m,reg=new RegExp(text,"g");for(i=0;i<first.length;++i)(m=first[i].match(reg))&&m.length>0&&second.push(first[i]);for(i=0;i<second.length;++i)item=item.replace(second[i],second[i].replace(reg,"<strong>$&</strong>"));return item},render:function(items){var that=this,self=this,activeFound=!1,data=[],_category=that.options.separator;return $.each(items,function(key,value){key>0&&value[_category]!==items[key-1][_category]&&data.push({__type:"divider"}),!value[_category]||0!==key&&value[_category]===items[key-1][_category]||data.push({__type:"category",name:value[_category]}),data.push(value)}),items=$(data).map(function(i,item){if("category"==(item.__type||!1))return $(that.options.headerHtml||that.theme.headerHtml).text(item.name)[0];if("divider"==(item.__type||!1))return $(that.options.headerDivider||that.theme.headerDivider)[0];var text=self.displayText(item);return(i=$(that.options.item||that.theme.item).data("value",item)).find(that.options.itemContentSelector||that.theme.itemContentSelector).addBack(that.options.itemContentSelector||that.theme.itemContentSelector).html(that.highlighter(text,item)),this.followLinkOnSelect&&i.find("a").attr("href",self.itemLink(item)),i.find("a").attr("title",self.itemTitle(item)),text==self.$element.val()&&(i.addClass("active"),self.$element.data("active",item),activeFound=!0),i[0]}),this.autoSelect&&!activeFound&&(items.filter(":not(.dropdown-header)").first().addClass("active"),this.$element.data("active",items.first().data("value"))),this.$menu.html(items),this},displayText:function(item){return void 0!==item&&void 0!==item.name?item.name:item},itemLink:function(item){return null},itemTitle:function(item){return null},next:function(event){var next=this.$menu.find(".active").removeClass("active").next();next.length||(next=$(this.$menu.find($(this.options.item||this.theme.item).prop("tagName"))[0])),next.addClass("active");var newVal=this.updater(next.data("value"));this.$element.val(this.displayText(newVal)||newVal)},prev:function(event){var prev=this.$menu.find(".active").removeClass("active").prev();prev.length||(prev=this.$menu.find($(this.options.item||this.theme.item).prop("tagName")).last()),prev.addClass("active");var newVal=this.updater(prev.data("value"));this.$element.val(this.displayText(newVal)||newVal)},listen:function(){this.$element.on("focus.bootstrap3Typeahead",$.proxy(this.focus,this)).on("blur.bootstrap3Typeahead",$.proxy(this.blur,this)).on("keypress.bootstrap3Typeahead",$.proxy(this.keypress,this)).on("propertychange.bootstrap3Typeahead input.bootstrap3Typeahead",$.proxy(this.input,this)).on("keyup.bootstrap3Typeahead",$.proxy(this.keyup,this)),this.eventSupported("keydown")&&this.$element.on("keydown.bootstrap3Typeahead",$.proxy(this.keydown,this));var itemTagName=$(this.options.item||this.theme.item).prop("tagName");"ontouchstart"in document.documentElement?this.$menu.on("touchstart",itemTagName,$.proxy(this.touchstart,this)).on("touchend",itemTagName,$.proxy(this.click,this)):this.$menu.on("click",$.proxy(this.click,this)).on("mouseenter",itemTagName,$.proxy(this.mouseenter,this)).on("mouseleave",itemTagName,$.proxy(this.mouseleave,this)).on("mousedown",$.proxy(this.mousedown,this))},destroy:function(){this.$element.data("typeahead",null),this.$element.data("active",null),this.$element.unbind("focus.bootstrap3Typeahead").unbind("blur.bootstrap3Typeahead").unbind("keypress.bootstrap3Typeahead").unbind("propertychange.bootstrap3Typeahead input.bootstrap3Typeahead").unbind("keyup.bootstrap3Typeahead"),this.eventSupported("keydown")&&this.$element.unbind("keydown.bootstrap3-typeahead"),this.$menu.remove(),this.destroyed=!0},eventSupported:function(eventName){var isSupported=eventName in this.$element;return isSupported||(this.$element.setAttribute(eventName,"return;"),isSupported="function"==typeof this.$element[eventName]),isSupported},move:function(e){if(this.shown)switch(e.keyCode){case 9:case 13:case 27:e.preventDefault();break;case 38:if(e.shiftKey)return;e.preventDefault(),this.prev();break;case 40:if(e.shiftKey)return;e.preventDefault(),this.next()}},keydown:function(e){17!==e.keyCode&&(this.keyPressed=!0,this.suppressKeyPressRepeat=~$.inArray(e.keyCode,[40,38,9,13,27]),this.shown||40!=e.keyCode?this.move(e):this.lookup())},keypress:function(e){this.suppressKeyPressRepeat||this.move(e)},input:function(e){var currentValue=this.$element.val()||this.$element.text();this.value!==currentValue&&(this.value=currentValue,this.lookup())},keyup:function(e){if(!this.destroyed)switch(e.keyCode){case 40:case 38:case 16:case 17:case 18:break;case 9:if(!this.shown||this.showHintOnFocus&&!this.keyPressed)return;this.select();break;case 13:if(!this.shown)return;this.select();break;case 27:if(!this.shown)return;this.hide()}},focus:function(e){this.focused||(this.focused=!0,this.keyPressed=!1,this.options.showHintOnFocus&&!0!==this.skipShowHintOnFocus&&("all"===this.options.showHintOnFocus?this.lookup(""):this.lookup())),this.skipShowHintOnFocus&&(this.skipShowHintOnFocus=!1)},blur:function(e){this.mousedover||this.mouseddown||!this.shown?this.mouseddown&&(this.skipShowHintOnFocus=!0,this.$element.focus(),this.mouseddown=!1):(this.select(),this.hide(),this.focused=!1,this.keyPressed=!1)},click:function(e){e.preventDefault(),this.skipShowHintOnFocus=!0,this.select(),this.$element.focus(),this.hide()},mouseenter:function(e){this.mousedover=!0,this.$menu.find(".active").removeClass("active"),$(e.currentTarget).addClass("active")},mouseleave:function(e){this.mousedover=!1,!this.focused&&this.shown&&this.hide()},mousedown:function(e){this.mouseddown=!0,this.$menu.one("mouseup",function(e){this.mouseddown=!1}.bind(this))},touchstart:function(e){e.preventDefault(),this.$menu.find(".active").removeClass("active"),$(e.currentTarget).addClass("active")},touchend:function(e){e.preventDefault(),this.select(),this.$element.focus()}};var old=$.fn.typeahead;$.fn.typeahead=function(option){var arg=arguments;return"string"==typeof option&&"getActive"==option?this.data("active"):this.each(function(){var $this=$(this),data=$this.data("typeahead"),options="object"==typeof option&&option;data||$this.data("typeahead",data=new Typeahead(this,options)),"string"==typeof option&&data[option]&&(arg.length>1?data[option].apply(data,Array.prototype.slice.call(arg,1)):data[option]())})},Typeahead.defaults={source:[],items:8,minLength:1,scrollHeight:0,autoSelect:!0,afterSelect:$.noop,afterEmptySelect:$.noop,addItem:!1,followLinkOnSelect:!1,delay:0,separator:"category",theme:"bootstrap3",themes:{bootstrap3:{menu:'<ul class="typeahead dropdown-menu" role="listbox"></ul>',item:'<li><a class="dropdown-item" href="#" role="option"></a></li>',itemContentSelector:"a",headerHtml:'<li class="dropdown-header"></li>',headerDivider:'<li class="divider" role="separator"></li>'},bootstrap4:{menu:'<div class="typeahead dropdown-menu" role="listbox"></div>',item:'<button class="dropdown-item" role="option"></button>',itemContentSelector:".dropdown-item",headerHtml:'<h6 class="dropdown-header"></h6>',headerDivider:'<div class="dropdown-divider"></div>'}}},$.fn.typeahead.Constructor=Typeahead,$.fn.typeahead.noConflict=function(){return $.fn.typeahead=old,this},$(document).on("focus.typeahead.data-api",'[data-provide="typeahead"]',function(e){var $this=$(this);$this.data("typeahead")||$this.typeahead($this.data())})});
