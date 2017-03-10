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

	//console.log(src.query());

	  $scope.customer = {
	    name: 'Naomi',
	    address: '1600 Amphitheatre'
	  };
}])
.directive('tryNav', function(Parameter,$cookies, $location) {
  return {
  	restrict: "E",
    templateUrl: '/api/templates/try-nav.html',
    link: function (scope, element, attr) { 
            
            scope.items = Parameter.get({"family":"Acadia","critical":"False"})
            console.log('requery');

            scope.selectItem = function($family){
                // console.log('tryNav directive :'+$family)
                $location.path("/distribute/" + $family) // $item.slug was added after completion of content
                // scope.searchQuery = ""
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