from rest_framework.serializers import (
	ModelSerializer,
	HyperlinkedIdentityField,
	SerializerMethodField
	)

from stations.api.serializers import StationListSerializer
# from comments.api.serializers import CommentSerializer
# from comments.models import Comment


from production.models import Parameter


# class PostCreateUpdateSerializer (ModelSerializer):
# 	class Meta:
# 		model = Post
# 		fields =[
# 			# 'id',
# 			'title',
# 			# 'slug',
# 			'content',
# 			'publish'
# 		]

# post_detail_url=HyperlinkedIdentityField(
# 		view_name='posts-api:detail',
# 		lookup_field='slug'
# 		)

# class PostDetailSerializer (ModelSerializer):
# 	url=post_detail_url
# 	user = UserDetailSerializer(read_only=True) #SerializerMethodField()
# 	#UserDetailSerializer(read_only=True)#
# 	image = SerializerMethodField()
# 	html = SerializerMethodField()
# 	comments=SerializerMethodField()
# 	class Meta:
# 		model = Post
# 		fields =[
# 			'url',
# 			'user',
# 			'id',
# 			'title',
# 			'slug',
# 			'content',
# 			'html',
# 			'publish',
# 			'image',
# 			'comments'
# 		]
# 	def get_html(self,obj):
# 		return obj.get_markdown()

# 	# def get_user(self,obj):
# 	# 	return str(obj.user.username)

# 	def get_image(self,obj):
# 		try:
# 			image=obj.image.url
# 		except:
# 			image = None
# 		return image

# 	def get_comments(self,obj):
# 		# content_type = obj.get_content_type
# 		# object_id=obj.id
# 		c_qs = Comment.objects.filter_by_instance(obj)
# 		comments = CommentSerializer(c_qs,many=True).data
# 		return comments

class ParameterListSerializer (ModelSerializer):

	# delete_url=HyperlinkedIdentityField(
	# 	view_name='posts-api:delete',
	# 	lookup_field='slug'
	# 	)
	# print ("PostListSerializer...start")
	# url=post_detail_url
	station = StationListSerializer(read_only=True)#SerializerMethodField()
	#UserDetailSerializer(read_only=True)#
	class Meta:
		model = Parameter
		fields =[
			'name',
			'description',
			# 'units',
			# 'created_date',
			# 'modified_date',
			# 'user',
			'activated',
			'critical',
			'ordering',
			'attribute',
			'station'
		]


class ParameterLiteListSerializer (ModelSerializer):

	# delete_url=HyperlinkedIdentityField(
	# 	view_name='posts-api:delete',
	# 	lookup_field='slug'
	# 	)
	# print ("PostListSerializer...start")
	# url=post_detail_url
	# station = StationListSerializer(read_only=True)#SerializerMethodField()
	#UserDetailSerializer(read_only=True)#
	class Meta:
		model = Parameter
		fields =[
			'name',
			'description',
			# 'units',
			# 'created_date',
			# 'modified_date',
			# 'user',
			'activated',
			'critical',
			'ordering',
			'attribute',
			'station'
		]


