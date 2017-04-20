'use strict';

angular.
    module('export').
        factory('Export', function($resource){
            // return 'hello Family'
            // console.log('Family function execute')
            var url = '/export/'
            return $resource(url, {}, {
                "query": {
                    method: "GET",
                    params: {},
                    isArray: true,
                    cache: false,
                    transformResponse: function(data, headersGetter, status){
                        var finalData = angular.fromJson(data)
                        return finalData
                        //finalData.results
                    }
                    // interceptor
                },
                "get": {
                    method: "GET",
                    // params: {"slug": "@slug"},
                    params: {},
                    isArray: true,
                    cache: false,
                    // transformResponse: function(data, headersGetter, status){
                    //     var finalData = angular.fromJson(data)
                    //     return finalData
                    //     //finalData.results
                    // }
                    // // transformResponse: function(data, headersGetter, status){
                    //     // console.log(data)
                    //     var finalData = angular.fromJson(data)
                    //     console.log (finalData)
                    //     return finalData
                    //     //finalData.results
                    // }
                }
            })
            
        });
