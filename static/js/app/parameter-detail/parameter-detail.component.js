'use strict';

angular.module('parameterDetail').
    component('parameterDetail', {
        templateUrl: '/api/templates/parameter-detail.html',
        controller:['$cookies', '$location', '$routeParams', '$rootScope', '$scope','$resource', 
        function($cookies, $location, $routeParams, $rootScope, $scope,$resource){
            var family = $routeParams.model
            var station = $routeParams.station
            var parameter = $routeParams.parameter
            var range = $routeParams.range
            $scope.family = family
            $scope.station = station
            $scope.parameter = parameter
            $scope.range = '7day'

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
          
        }]
    });