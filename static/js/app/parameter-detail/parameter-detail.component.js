'use strict';

angular.module('parameterDetail').
    component('parameterDetail', {
        templateUrl: '/api/templates/parameter-detail.html',
        controller:['Parameter','$cookies', '$location', '$routeParams', '$rootScope', '$scope','$resource', 
        function(Parameter,$cookies, $location, $routeParams, $rootScope, $scope,$resource){
            var family = $routeParams.model
            var station = $routeParams.station
            var parameter = $routeParams.parameter
            var range = $routeParams.range
            $scope.family = family
            $scope.station = station
            $scope.parameter = parameter
            $scope.range = '7day'
            // $scope.searchQuery=parameter

            $scope.ToSlash = function(item){
                // var name=item.name;
                var new_name = item.replace("/","-slash-")
                return new_name;
            };

            $scope.removeSlash = function(item){
                // var name=item.name;
                console.log(item);
                // var new_name = item.replace("-slash-","/")
                return item;
            };
            
            $scope.replaceStr = function(x) {
                   return x.replace("-slash-","/")
             };


             $scope.dateClick = function (active) { 
                console.log(active.currentTarget.value);
                $scope.range = active.currentTarget.value
            };


             $scope.getButtonClass = function(range){
                var x = (range === $scope.range);
                // console.log(x)
                if (x){
                    return "btn btn-primary"
                }
                else {
                    return "btn btn-default"
                }
            }

            $scope.selectParameter = function($item, $model, $label){
                var selectedParam = $item.name.replace("/","-slash-");
                var selectedStation = $item.station.station;
                $scope.station = selectedStation
                $scope.parameter = selectedParam
                $scope.searchQuery=""
                // console.log($item)
                // $location.path("/distribute/" + scope.family + "/" + selectedStation +"/" + selectedParam) // $item.slug was added after completion of content
                // scope.items = Parameter.get_lite({"family":$family,"critical":"True"})
                // console.log('requery parameter for ' + selectedParam + selectedStation + scope.family );
                // scope.searchQuery = ""
            }

            $scope.getImageSrc = function(parameter,range){
                // $scope.station = station
                var boxplot_scr = "dashboard/graph/boxplot/" + family +"/" + station + "/" + parameter + "/" + range + "/"
                var hist_scr = "dashboard/graph/histogram/" + family +"/" + station + "/" + parameter + "/" + range + "/"
                // console.log(new_scr)
                return {
                    "boxplot":boxplot_scr,
                    "histogram" : hist_scr
                }
            }

            if (station && family){
                  var param_kwarg={"family":family,"station":station};
                                       
                  Parameter.get(param_kwarg,function(parameters) {
                    //do something with todos
                    $scope.parameters = parameters
                    angular.forEach(parameters, function(parameter) {
                       if (true){
                          // console.log(parameter.description);
                          }
                    });
                  });
            }//End if
          
        }]
    });