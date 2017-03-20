'use strict';


// .controller('Controller', ['$scope','$resource','Family',function($scope,$resource,Family) {

angular.module('spcStationDetail').
    component('spcStationDetail', {
        templateUrl: '/api/templates/spc-station-detail.html',
        controller:['Tester','Station','Parameter','$cookies', '$location', '$routeParams', '$rootScope', '$scope','$resource', 
        function(Tester,Station,Parameter,$cookies, $location, $routeParams, $rootScope, $scope,$resource){
            var family = $routeParams.model
            var station = $routeParams.station
            var tester = $routeParams.tester
            var range = $routeParams.range
            $scope.model=family
            $scope.tester = tester
            $scope.showDateRange=false
            $scope.range = 'slot'
            console.log(tester)

            var from_path=location.pathname.replace("/","");
            from_path=from_path.split('/');
            $scope.from_path = from_path[0];
            // console.log(from_path[0] + ' On spc station')
             

            

            if (family){
                var station_kwrg={"family":family};
                var tester_kwrg={"onlytester":"True","family":family};
                
                if (from_path[0]=='spc'){
                        station_kwrg={"family":family,"spc":"true"}
                }

                if (station) {
                    station_kwrg={"family":family,"station" : station}
                    if (from_path[0]=='spc'){
                        station_kwrg={"family":family,"station" : station,"spc":"true"}
                    }
                    // console.log(station_kwrg)
                    $scope.showDateRange=true
                }

                  Station.get(station_kwrg,function(stations) {
                    //do something with todos
                    $scope.stations = stations
                    angular.forEach(stations, function(station) {
                       if (true){
                        // console.log(station.family);
                          }
                    });
                  });

                  Tester.get(tester_kwrg,function(testers) {
                    $scope.testers = testers
                    // console.log(testers)
                  });

                  
                var param_kwarg = {"family":family,"critical":"True"};
                // if (from_path[0]=='spc'){
                //         param_kwarg={"family":family,"spc":"true"}
                //     }

                if (station){
                    param_kwarg={"family":family,"station":station,"critical":"True"};
                    if (from_path[0]=='spc'){
                        param_kwarg={"family":family,"station" : station,"spc":"true"}
                        // console.log(station_kwrg)
                    }
                    $scope.showDateRange=true
                    }
                    
                  Parameter.get(param_kwarg,function(parameters) {
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

            $scope.$watch('range',function(){
                // console.log('range change')
            });

            $scope.dateClick = function (active) { 
                
                $scope.range = active.currentTarget.value
                // console.log(active.currentTarget.value)
                if (active.currentTarget.value=='slot'){
                    var item_kwrg={"family":family,"station":station,"tester":tester};
                    Tester.get(item_kwrg,function(testers) {
                        $scope.selectItems = testers
                        // console.log(testers)
                      });
                    }

                if (active.currentTarget.value=='parameter'){
                    var item_kwrg={"family":family,"station":station,"spc_control":"True"};
                    Parameter.get(item_kwrg,function(parameters) {
                        $scope.selectItems = parameters
                        // console.log(parameters)
                      });
                    }
            };

            $scope.getImageSrc = function(station,parameter,range){
                $scope.staton = station
                var boxplot_scr = "dashboard/graph/boxplot/" + family +"/" + station + "/" + parameter + "/" + range + "/"
                var hist_scr = "dashboard/graph/histogram/" + family +"/" + station + "/" + parameter + "/" + range + "/"
                // console.log(new_scr)
                return {
                    "boxplot":boxplot_scr,
                    "histogram" : hist_scr
                }
            }

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

        }]
    });