'use strict';

angular.
    module('core.post').
        factory('Post', function($resource){
            var url = '/api/station/:family/'
            return $resource(url, {}, {
                query: {
                    method: "GET",
                    params: {},
                    isArray: true,
                    cache: false,
                    transformResponse: function(data, headersGetter, status){
                        // console.log(data)
                        var finalData = angular.fromJson(data)
                        return finalData.results
                    }
                    // interceptor
                },
                get: {
                    method: "GET",
                    params: {"family": "@family"},
                    isArray: false,
                    cache: false,
                }
            })

        });