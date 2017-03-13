'use strict';


// .controller('Controller', ['$scope','$resource','Family',function($scope,$resource,Family) {

angular.module('modelList').
    component('modelList', {
        templateUrl: '/api/templates/model-list.html',
        controller:['Station','Parameter','$cookies', '$location', '$routeParams', '$rootScope', '$scope','$resource', 
        function(Station,Parameter,$cookies, $location, $routeParams, $rootScope, $scope,$resource){
            var family = $routeParams.model
            $scope.model=family
            // console.log(Station)

            if (family){
                  Station.get({"family":family},function(stations) {
                    //do something with todos
                    $scope.stations = stations
                    angular.forEach(stations, function(station) {
                       if (true){
                        // console.log(station.family);
                          }
                    });
                  });

                  Parameter.get({"family":family,"critical":"True"},function(parameters) {
                    //do something with todos
                    $scope.parameters = parameters
                    angular.forEach(parameters, function(parameter) {
                       if (true){
                         // console.log(parameter.description);
                          }
                    });
                  });


            }

            $scope.currStation = function (item) { 
                return item.station;
            };

            $scope.ToSlash = function(item){
                var name=item.name;
                var new_name = name.replace("/","-slash-")
                return new_name;
            }

            // console.log($location.search())
            // var q = $location.search().q
            // console.log(q)
            // if (q) {
            //     $scope.query = q
            //     $scope.didPerformSearch = true;
            // }

            // $scope.order = '-publish'
            // $scope.goToItem = function(post){
            //     $rootScope.$apply(function(){
            //         $location.path("/blog/" + post.id )
            //     })
            // }

            // $scope.changeCols = function(number){
            //     if (angular.isNumber(number)){
            //         $scope.numCols = number
            //     } else {
            //         $scope.numCols = 2
            //     }
            //     setupCol($scope.items, $scope.numCols)
            // }

            // $scope.loadingQuery = false
            // $scope.$watch(function(){
            //     // console.log($scope.query)
            //     if($scope.query) {
            //         $scope.loadingQuery = true
            //         $scope.cssClass = 'col-sm-12'
            //         if ($scope.query != q) {
            //             $scope.didPerformSearch = false;
            //         }
            //     } else {
            //         if ($scope.loadingQuery) {
            //             setupCol($scope.items, 2)
            //             $scope.loadingQuery = false
            //         }
                     
            //     }

            // })

            // function setupCol(data, number){
            //     if (angular.isNumber(number)){
            //         $scope.numCols = number
            //     } else {
            //         $scope.numCols = 2
            //     }
            //     $scope.cssClass = 'col-sm-' + (12/$scope.numCols)
            //     $scope.items = data
            //     $scope.colItems = chunkArrayInGroups(data, $scope.numCols)
            // }

            // Post.query(function(data){
            //         setupCol(data, 2)
            //     }, function(errorData){

            // });

            // function chunkArrayInGroups(array, unit) {
            //     var results = [],
            //     length = Math.ceil(array.length / unit);
            //     for (var i = 0; i < length; i++) {
            //         results.push(array.slice(i * unit, (i + 1) * unit));
            //     }
            //     return results;
            // }

        }]
    });