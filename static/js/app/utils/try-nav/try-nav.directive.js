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
.controller('Controller', ['$scope','$resource','Family',function($scope,$resource,Family) {
	Family.get({},function(todos) {
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
                $location.path("/distribute/" + $family) // $item.slug was added after completion of content
                scope.items = Parameter.get({"family":$family,"critical":"True"})
                scope.family= $family;
                console.log('selectFamily : requery parameter for ' + $family);
                // scope.searchQuery = ""
            }

            scope.selectParameter = function($item, $model, $label){
                var selectedParam = $item.name.replace("/","-slash-");
                var selectedStation = $item.station.station;
                //console.log($item)
                $location.path("/distribute/" + scope.family + "/" + selectedStation +"/" + selectedParam) // $item.slug was added after completion of content
                // scope.items = Parameter.get_lite({"family":$family,"critical":"True"})
                // console.log('requery parameter for ' + selectedParam + selectedStation + scope.family );
                scope.searchQuery = ""
            }

            

            // scope.seachItem = function(){
            //     console.log(scope.searchQuery)
            //     $location.path("/blog/").search("q", scope.searchQuery)
            //     scope.searchQuery = ""
            // }

            // scope.userLoggedIn = false
            // scope.$watch(function(){
            //     var token = $cookies.get("token")
            //     if (token) {
            //         scope.userLoggedIn = true
            //     } else {
            //         scope.userLoggedIn = false
            //     }
            // })
        } //end link
  };
});


// .controller('Controller', ['$scope', function($scope,Family) {

//   $scope.customer = {
//     name: 'Naomi',
//     address: '1600 Amphitheatre'
//   };
// }])

	// Family.query({}, function(data){
 //                    // console.log(data)
 //                    $scope.comments = data
 //                })
 // Family.query(function(data){
 //                   console.log(data)
 //                }, function(errorData){

 //            });