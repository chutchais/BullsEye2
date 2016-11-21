from django.db import models

# Create your models here.
#Master data
class Bom(models.Model):
	name = models.CharField(max_length=50,primary_key=True)
	model = models.CharField(verbose_name ='Model Name',max_length=50)
	rev = models.CharField(verbose_name ='Model Revision',max_length=50)
	description = models.CharField(max_length=255)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)

	def __str__(self):
		return self.name

	class Meta:
		unique_together = ('model', 'rev')


class BomDetails(models.Model):
	bom = models.ForeignKey('Bom',
		on_delete = models.CASCADE, related_name='bom_details')
	pn = models.CharField(verbose_name ='Part Number',max_length=50)
	customer_pn = models.CharField(verbose_name ='Customer Part number' ,max_length=50)
	rd = models.CharField(verbose_name ='Reference Destination' , max_length=50)
	description = models.CharField(max_length=255)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)

	def __str__(self):
		return self.pn

class Family(models.Model):
	name = models.CharField(max_length=50,primary_key=True,db_index=True)
	description = models.CharField(max_length=255)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)
	critical = models.BooleanField(verbose_name ='Critical Family?',default=False)
	ordering = models.IntegerField(default=1)

	def __str__(self):
		return self.name

class Product(models.Model):
	name = models.CharField(max_length=50,db_index=True)
	model = models.CharField(verbose_name ='Model Name',max_length=50,db_index=True)
	rev = models.CharField(verbose_name ='Model Revision',max_length=50)
	customer_model = models.CharField(verbose_name ='Customer Model',max_length=50)
	customer_rev = models.CharField(verbose_name ='Customer Model revision',max_length=50)
	group = models.CharField(verbose_name ='Product Group',max_length=50)
	bom = models.ForeignKey('Bom' ,related_name='product_used',null=True)
	family = models.ForeignKey('Family' ,related_name='product_used',null=True)
	description = models.CharField(max_length=255)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)

	def __str__(self):
		return self.name




class Station(models.Model):
	"""docstring for ClassName"""
	station = models.CharField(verbose_name ='Station number',max_length=50,db_index=True)
	name = models.CharField(verbose_name ='Station name',max_length=50,blank=True, null=True)
	description = models.CharField(max_length=255,blank=True, null=True)
	family = models.ForeignKey('Family' ,related_name='station_used',null=True)
	process = models.CharField(max_length=255,blank=True, null=True)
	first_process = models.BooleanField(verbose_name ='First process station?',default=False)
	last_process = models.BooleanField(verbose_name ='Last process station?',default=False)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)
	critical = models.BooleanField(verbose_name ='Critical station?',default=False)
	ordering = models.IntegerField(default=1)
	
	def __str__(self):
		return ('%s : %s' % (self.station,self.name))


class Routing(models.Model):
	"""docstring for ClassName"""
	name = models.CharField(max_length=50,db_index=True)
	description = models.CharField(max_length=255)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)
	
	def __str__(self):
		return self.name


class RoutingDetails(models.Model):
	"""docstring for ClassName"""
	route = models.ForeignKey('Routing' ,related_name='route_details')
	station = models.ForeignKey('Station' ,related_name='route_used')
	description = models.CharField(max_length=255)
	next_pass = models.ForeignKey('Station' ,related_name='route_used_next_pass')
	next_fail = models.ForeignKey('Station' ,related_name='route_used_next_fail')
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)
	
	def __str__(self):
		return self.station.name

#Configuration data
class WorkOrder(models.Model):
	PROD = 'PROD'
	RMA='RMA'
	QUAL='QUAL'
	BUILD_TYPE_CHOICES = (
        (PROD, 'Production'),
        (RMA, 'Repair'),
        (QUAL,'Qualification')
    )
	name = models.CharField(max_length=50,db_index=True)
	description = models.CharField(max_length=255)
	product = models.ForeignKey('Product' ,related_name='workorder_used')
	qty = models.IntegerField(default=1)
	build_type = models.CharField(max_length=10 ,choices=BUILD_TYPE_CHOICES,default=PROD)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)

	def __str__(self):
		return self.name

	def registered(self):
		return self.sn_list.count()

	def inprocess(self):
		return self.sn_list.filter(status='IN').count()

	def completed(self):
		return self.sn_list.filter(status='DONE').count()

	def shipped(self):
		return self.sn_list.filter(status='SHIPPED').count()





class WorkOrderDetails(models.Model):
	IN = 'IN'
	DONE = 'DONE'
	SHIPPED = 'SHIPPED'
	STATUS_CHOICES = (
        (IN, 'In Process'),
        (DONE, 'Completed Process'),
        (SHIPPED, 'Shipped'),
    )
	sn = models.CharField(max_length=50,db_index=True)
	workorder = models.ForeignKey('WorkOrder' ,related_name='sn_list',db_index=True)
	created_date = models.DateTimeField(auto_now_add=True,db_index=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True,db_index=True)
	current_station = models.ForeignKey('Station' ,related_name='sn_current_station',blank=True,null=True,db_index=True)
	last_station = models.ForeignKey('Station' ,related_name='sn_last_station',blank=True,null=True,db_index=True)
	result = models.BooleanField(default=True) #Last Result Pass/Fail
	status = models.CharField(max_length=50,choices=STATUS_CHOICES,default=IN,db_index=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)
	# created_date = models.DateTimeField(auto_now_add=True)
	# modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	
	def __str__(self):
		return "%s on %s" % (self.sn,self.workorder)


class Performing(models.Model):
	sn_wo = models.ForeignKey('WorkOrderDetails' ,related_name='performing_list',db_index=True)
	station = models.ForeignKey('Station' ,related_name='perform_station',blank=True,null=True,db_index=True)
	loop = models.IntegerField(default=1,db_index=True)
	started_date = models.DateTimeField(db_index=True)
	finished_date = models.DateTimeField()
	tester = models.CharField(max_length=100,blank=True,null=True,db_index=True)
	result = models.BooleanField(default=True,db_index=True)
	dispose_code = models.CharField(max_length=100,db_index=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)

	def __str__(self):
		return "%s" % self.sn_wo


class Parameter(models.Model):
	name = models.CharField(max_length=255,db_index=True)
	units = models.CharField(max_length=50,blank=True, null=True)
	group = models.CharField(max_length=50,db_index=True)
	description = models.CharField(max_length=255)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)
	activated = models.BooleanField(default=True)
	critical = models.BooleanField(verbose_name ='Critical station?',default=False)
	ordering = models.IntegerField(default=1)
	
	def __str__(self):
		return ("%s" % (self.description))
		# return ("%s : %s" % (self.name,self.description))


class PerformingDetails(models.Model):
	S = 'String'
	N = 'Number'
	VALUE_CHOICES = (
        (S, 'String'),
        (N, 'Number'),
    )
	performing = models.ForeignKey('Performing' ,related_name='performingdetail_list')
	parameter = models.ForeignKey('Parameter' ,related_name='performing_used',db_index=True)
	value = models.FloatField(null=True, blank=True)
	value_str = models.CharField(max_length=255,null=True, blank=True)
	limit_min = models.FloatField(null=True, blank=True)
	limit_max = models.FloatField(null=True, blank=True)
	value_type = models.CharField(max_length=10,choices=VALUE_CHOICES,default=S)
	result = models.BooleanField(default=True,db_index=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)
	created_date = models.DateTimeField()
	
	def __str__(self):
		return self.parameter.name

	def extract_date(self):
		return self.created_date.date()



#Models for DA and ECO Projects.
class DocumentControls(models.Model):
	OPEN = 'OPEN'
	CLOSE = 'CLOSE'
	PENDING = 'PENDING'
	DA = 'DA'
	ECO = 'ECO'
	STATUS_CHOICES = (
		(OPEN, 'Opened'),
		(CLOSE, 'Closed'),
		(PENDING, 'Pending'),)
	DOCUMENT_TYPE_CHOICE = (
		(DA,'DA'),
		(ECO,'ECO'),
	)
	doc_number = models.CharField(max_length=255,db_index=True)
	doc_type = models.CharField(max_length=50,choices=DOCUMENT_TYPE_CHOICE,default=DA,db_index=True)
	title = models.CharField(max_length=255)
	details = models.CharField(max_length=4000)
	received_date = models.DateField(blank=True, null=True)
	initial_date = models.DateField(blank=True, null=True)
	expire_date = models.DateField(blank=True, null=True)
	finished_date = models.DateField(blank=True, null=True)
	bom_process = models.IntegerField(default=0)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(blank=True, null=True,auto_now=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)
	status = models.CharField(max_length=50,choices=STATUS_CHOICES,default=OPEN,db_index=True)
	
	def log_total(self):
		return ('%s' % self.logs.all().count())

	def document_total(self):
		return ('%s' % self.related_list.all().count())

	def __str__(self):
		return ("%s" % (self.doc_number))

class DocumentLogs(models.Model):
	doc_number = models.ForeignKey('DocumentControls' ,related_name='logs',db_index=True)
	details = models.CharField(max_length=4000)
	created_date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)

class DocumentRelated(models.Model):
	FAMILY='FAMILY'
	PRODUCT='PRODUCT'
	GOLF='GOLF'
	ITEM_TYPE_CHOICE = (
		(FAMILY,'Family'),
		(PRODUCT,'Product'),
		(GOLF,'Golf')
	)
	doc_number = models.ForeignKey('DocumentControls' ,related_name='related_list',db_index=True)
	item = models.CharField(max_length=50)
	item_type =models.CharField(max_length=50,choices=ITEM_TYPE_CHOICE,default=PRODUCT,db_index=True)
	details = models.CharField(max_length=255)
	created_date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)


class Components(models.Model):
	part_id = models.CharField(max_length=50,primary_key=True)
	part_no = models.CharField(max_length=100,db_index=True)
	mfg_name =models.CharField(max_length=100)
	mfg_partno =models.CharField(max_length=100,db_index=True)
	mfg_lotcode= models.CharField(max_length=50,db_index=True)
	mfg_datecode = models.CharField(max_length=50,db_index=True)
	rtno = models.CharField(max_length=50,db_index=True)
	created_date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)

	def __str__(self):
		return ("%s" % (self.part_no))


class ComponentsTracking(models.Model):
	ACTIVE = 'ACTIVE'
	REMOVE = 'REMOVE'
	STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (REMOVE, 'Removed'),
    )
	part = models.ForeignKey('Components' ,related_name='component_list')
	sn_wo = models.ForeignKey('WorkOrderDetails' ,related_name='component_tracking')
	rd = models.CharField(max_length=50,db_index=True)
	station = models.ForeignKey('Station' ,related_name='component_part',blank=True,null=True,db_index=True)
	status = models.CharField(max_length=10,choices=STATUS_CHOICES,default=ACTIVE)
	created_date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey('auth.User',blank=True,null=True)

	def __str__(self):
		return ("%s" % (self.rd))
