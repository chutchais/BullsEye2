'use strict';
// angular.module("tryNav").
// directive('tryNav', function(){
//     return {    
//         restrict: "E",
//         templateUrl: "/api/templates/try-nav.html",
//         link : function(Family,scope,element,attr){
        	
//         }
//             }

// }).
// controller('Controller',function(){
// 	$scope.customer = 'test'
// });

angular.module('tryNav', [])
.controller('Controller', ['$location','$scope','$resource','Family',function($location,$scope,$resource,Family) {
	
    // console.log(location.pathname.replace("/",""));
    var from_path=location.pathname.replace("/","");
    from_path=from_path.split('/')
    $scope.from_path = from_path[0];

    var kwarg ={}
    if (from_path[0]=='spc'){
        kwarg={"spc":"true"}
    }

    Family.get(kwarg,function(todos) {
		  //do something with todos
		  // console.log(todos);

		  $scope.familys=todos
		  // angular.forEach(todos, function(todo) {
		  //    if (todo.critical){
		  //    	console.log(todo.name);
		 	//   }
		  // });
		  
		});

        function ToSlash(item){
                // var name=item.name;
                var new_name = item.replace("/","-slash-")
                return new_name;
        }
}])
.directive('tryNav', function(Parameter,$cookies, $location) {
  return {
  	restrict: "E",
    templateUrl: '/api/templates/try-nav.html',
    link: function (scope, element, attr) { 
            
            // scope.items = Parameter.get_lite({"family":"Acadia"})
            // console.log('requery');
            scope.selectFamily = function($family){
                // console.log('tryNav directive :'+$family)
                var new_path ='';
                var kwarg_parameter={"family":$family,"critical":"True"}

                if (scope.from_path=='') {
                    new_path="/distribute/" + $family
                }
                if (scope.from_path=='spc') {
                    new_path="/spc/" + $family
                    kwarg_parameter={"family":$family,"spc":"True"}
                }

                $location.path(new_path) // $item.slug was added after completion of content

                // console.log(kwarg_family)
                scope.items = Parameter.get(kwarg_parameter)
                scope.family= $family;
                // console.log('selectFamily : requery parameter for ' + $family);
                // scope.searchQuery = ""
            }

            scope.selectParameter = function($item, $model, $label){
                var selectedParam = $item.name.replace("/","-slash-");
                var selectedStation = $item.station.station;
                var new_path ='';
                if (scope.from_path=='') {
                    new_path="/distribute/" + scope.family + "/" + selectedStation +"/" + selectedParam
                }
                if (scope.from_path=='spc') {
                    new_path="/spc/" + scope.family + "/" + selectedStation +"/" + selectedParam
                }

                //console.log($item)
                $location.path(new_path) // $item.slug was added after completion of content
                // scope.items = Parameter.get_lite({"family":$family,"critical":"True"})
                // console.log('requery parameter for ' + selectedParam + selectedStation + scope.family );
                scope.searchQuery = ""
            }


        } //end link
  };
});


