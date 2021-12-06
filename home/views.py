from django.shortcuts import render
from .models import *
from .forms import *
from django.http import JsonResponse
from django.db.models.functions import Lower
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import json


def home(request):
  return render(request,'home/home.html',{})

def permission_not_granted(request):
    return render(request,'403.html')

def handler404(request,exception,template_name='404.html'):
    return render(request,template_name)
	
def handler500(request):
    return render(request,'500.html')


COMPANY_COUNT=70
@login_required
def charts(request):

	branches = ["CSE", "MNC", "EE", "ME", "CE", "CL", "EP", "CST", "BT", "DS","Physics", "Chemistry", "Mathematics", "Design", "Others"]
	dens_btech={"CSE":100,"MNC":66,"EE":146,"ME":100,"CL":67,"EP":47,"CST":45,"BT":44,"Design":45,"CE":84}
	dens_mtech={"CSE":66,"BT":51,"EE":90,"ME":123,"CE":123,"Design":31,"CL":60,"DS":20}
	dens_others={"M.A Humanities":54,"M.S Energy":15,"M.Sc Physics":56,"M.Sc Chemistry":59,"M.Sc Mathematics":58}
	btech_total=0
	mtech_total=0
	others_total=0
	for i in dens_btech:
		btech_total+=dens_btech[i]
	for i in dens_mtech:
		mtech_total+=dens_mtech[i]
	for i in dens_others:
		others_total+=dens_others[i]
	btech_all=Student.objects.filter(programs__in=['B.Tech','B.Des']).filter(placed=True)
	mtech_all=Student.objects.filter(programs__in=['M.Tech','M.Des']).filter(placed=True)
	others_all=Student.objects.filter(programs__in=['M.Sc','M.S',"M.A"]).filter(placed=True)

	btech_placed=len(btech_all)
	mtech_placed=len(mtech_all)
	others_placed=len(others_all)

	btech_percent_placed = json.dumps({"Placed": btech_placed, "Not placed": btech_total-btech_placed})
	mtech_percent_placed = json.dumps({"Placed": mtech_placed, "Not placed": mtech_total-mtech_placed})
	others_percent_placed = json.dumps({"Placed": others_placed, "Not placed": others_total-others_placed})

	comp_counts_btech={}
	comp_counts_mtech={}
	comp_counts_others={}

	for i in btech_all:
		if(i.company in comp_counts_btech):
			comp_counts_btech[i.company]+=1
		else:
			comp_counts_btech[i.company]=1

	for i in mtech_all:
		if(i.company in comp_counts_mtech):
			comp_counts_mtech[i.company]+=1
		else:
			comp_counts_mtech[i.company]=1

	for i in others_all:
		if(i.company in comp_counts_others):
			comp_counts_others[i.company]+=1
		else:
			comp_counts_others[i.company]=1

	comp_btech_counts=list(comp_counts_btech.values())
	comp_mtech_counts=list(comp_counts_mtech.values())
	comp_others_counts=list(comp_counts_others.values())

	comp_btech_counts.sort(reverse=True)
	comp_mtech_counts.sort(reverse=True)
	comp_others_counts.sort(reverse=True)

	btech_threshold=0
	mtech_threshold=0
	others_threshold=0

	if(len(comp_btech_counts)>COMPANY_COUNT):
		btech_threshold=comp_btech_counts[COMPANY_COUNT]
	if(len(comp_mtech_counts)>COMPANY_COUNT):
		mtech_threshold=comp_mtech_counts[COMPANY_COUNT]
	if(len(comp_others_counts)>COMPANY_COUNT):
		others_threshold=comp_others_counts[COMPANY_COUNT]

	comp_count_lis_btech=[]
	comp_count_lis_mtech=[]
	comp_count_lis_others=[]

	for i in comp_counts_btech:
		tmp={}
		if(i=="" or comp_counts_btech[i]<btech_threshold):
			continue
		tmp["tag"]=i
		tmp["weight"]=comp_counts_btech[i]
		tmp["urlval"]=i.replace(' ','%20')
		comp_count_lis_btech.append(tmp)

	for i in comp_counts_mtech:
		tmp={}
		if(i=="" or comp_counts_mtech[i]<mtech_threshold):
			continue
		tmp["tag"]=i
		tmp["weight"]=comp_counts_mtech[i]
		tmp["urlval"]=i.replace(' ','%20')
		comp_count_lis_mtech.append(tmp)

	for i in comp_counts_others:
		tmp={}
		if(i=="" or comp_counts_others[i]<others_threshold):
			continue
		tmp["tag"]=i
		tmp["weight"]=comp_counts_others[i]
		tmp["urlval"]=i.replace(' ','%20')
		comp_count_lis_others.append(tmp)

	btech_branchwise_placements=[]
	mtech_branchwise_placements = []
	others_branchwise_placements=[]

	for bch in branches:
		tmp={}
		tmp["group"]=bch
		if bch not in dens_btech:
			continue
		if(bch=="Design"):
			num=len(Student.objects.filter(programs='B.Des').filter(
				branch__branchName=bch).filter(placed=True))
			den = dens_btech[bch]
		elif(bch=="EE"):
			num = len(Student.objects.filter(programs='B.Tech').filter(
				branch__branchName__in=["ECE","EEE"]).filter(placed=True))
			den = dens_btech[bch]
		else:
			num = len(btech_all.filter(branch__branchName=bch))
			den = dens_btech[bch]
		if(num==0):
			continue
		tmp["value"] = round((num/den)*100,2)
		tmp["num"]=num
		tmp["den"]=den
		btech_branchwise_placements.append(tmp)

	for bch in branches:
		tmp = {}
		tmp["group"] = bch
		if bch not in dens_mtech:
			continue
		if(bch=="Design"):
			num=len(Student.objects.filter(programs='M.Des').filter(
				branch__branchName=bch).filter(placed=True))
			den = dens_mtech[bch]
		elif(bch=="EE"):
			num = len(Student.objects.filter(programs='M.Tech').filter(
				branch__branchName__in=["ECE","EEE"]).filter(placed=True))
			den = dens_mtech[bch]
		else:
			num = len(mtech_all.filter(branch__branchName=bch))
			den = dens_mtech[bch]
		if(num == 0):
			continue
		tmp["value"] = round((num/den)*100,2)
		tmp["num"]=num
		tmp["den"]=den
		mtech_branchwise_placements.append(tmp)

	for i in dens_others:
		bch=list(i.split())[1].strip()

		tmp = {}
		tmp["group"] = i
		if i not in dens_others:
			continue

		num = len(others_all.filter(branch__branchName=bch))
		den = dens_others[i]
		if(num == 0):
			continue
		tmp["value"] = round((num/den)*100,2)
		tmp["num"]=num
		tmp["den"]=den
		others_branchwise_placements.append(tmp)

	context = {"btech_percent_placed": btech_percent_placed,
			"mtech_percent_placed": mtech_percent_placed,
			"others_percent_placed":others_percent_placed,
			"btech_branchwise_placements": json.dumps(btech_branchwise_placements),
			"mtech_branchwise_placements": json.dumps(mtech_branchwise_placements),
			"others_branchwise_placements":json.dumps(others_branchwise_placements),
			"company_count":comp_count_lis_btech,
			"company_count_mtech":comp_count_lis_mtech,
			"company_count_others":comp_count_lis_others
			}

	return render(request, "home/stats.html",context )


################################################################################
# function to render the table

@login_required
def get_table(request):
	company = request.GET.get('company')
	if company:
		students  = Student.objects.filter(company=company)
	else:
		students  = Student.objects.filter(placed=True)

	branches = Branch.objects.all()
	context = {'students':students,'branches':branches}
	return render(request,'home/table_home.html',context)


################################################################################
# function to filter the table data

@login_required
def ajax_table_filter(request):
	data = dict()
	if request.method == 'GET' and request.is_ajax():
		branch = request.GET.get('branch')
		program = request.GET.get('program')
		sortid = request.GET.get('sortid')
		company = request.GET.get('company')
		students = Student.objects.filter(placed=True)
		if company:
			students= students.filter(company=company)
		if branch!='all':
			branch = Branch.objects.get(branchName=branch)
			students = students.filter(branch=branch)
		if program!='all':
			students = students.filter(programs=program)

		students = students.order_by(Lower(sortid))
		data['table_data_html'] = render_to_string('home/table_data.html',{'students':students})
		data['success'] = True
	else:
		data['success'] = False
	return JsonResponse(data)
################################################################################
