from bson import json_util
import re
import json
import os
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from elasticsearch import Elasticsearch		
from gnowsys_ndf.ndf.forms import SearchForm
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME,GSTUDIO_NO_OF_OBJS_PP

es = Elasticsearch(['http://elsearch:changeit@gsearch:9200'])
author_map = {}
group_map = {}

mapping_directory = '/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings'
if(os.path.isdir(mapping_directory)):
	with open(mapping_directory+'/authormap.json') as fe:
		author_map = json.load(fe)
	with open(mapping_directory+'/groupmap.json') as fe:
		group_map = json.load(fe)

else:
	print("No mapping found!")

hits = ""
med_list = []		 #contains all the search results
res_list = []		 #contains the header of the search results
results = []		 #contains a single page's results
altinfo_list = []
#GSTUDIO_SITE_NAME = "nroer_pro"
append_to_url = ""
author_index = "author_" + GSTUDIO_SITE_NAME
gsystemtype_index = "node_type_" + GSTUDIO_SITE_NAME

GROUP_CHOICES=["All"]
for name in group_map.keys():
    GROUP_CHOICES.append(name)
def get_search(request): 
	global med_list
	global res_list
	global results
	global append_to_url
	global altinfo_list
	form = SearchForm(request.GET)
	query = request.GET.get("query")
	form.query = query

	if(query):
		print(query)
		group = request.GET.get("group")
		chkl = request.GET.getlist("groupspec")
		print chkl
		if(len(chkl)>0):
			group = "All"
		print "query in group ", group
		page = request.GET.get("page")
		if(page is None):
			print(query)
			query_display = ""
			#group = request.GET.get('group')
			search_select = request.GET.get('search_select')
			search_filter = request.GET.getlist('checks[]')
			if(str(search_select) == '1'):
				append_to_url = ""
				select = "Author"
				resultSet = search_query(author_index, select, group, query)
				hits =  "<h3> No of docs found: <b>%d</b></h3> " % len(resultSet)
				med_list = get_search_results(resultSet)
				if(group == "All"):
					res_list = ['<h3>  Showing contributions of user <b>%s</b> in all groups:</h3> ' % (query), hits]
				else:
					res_list = ['<h3>  Showing contributions of user <b>%s</b> in group <b>%s</b>":</h3> ' % (query, group), hits]
				
			else:
				append_to_url = ""
				if(len(search_filter) == 0 or str(search_filter[0])=="all"):
					select = "Author,image,video,text,application,audio,Page,NotMedia,Group"
					append_to_url += "&checks%5B%5D=all"
				else:
					select = ""
					for i in range(0,len(search_filter)-1):
						select += search_filter[i]+"," 
						append_to_url += "&checks%5B%5D="+search_filter[i]
					append_to_url  += "&checks%5B%5D="+search_filter[len(search_filter) - 1]
					select += search_filter[len(search_filter) - 1]
				print(select)

				phsug_name = get_suggestion_body(query, field_value = "name.trigram", slop_value = 2, field_name_value = "name")
				phsug_content = get_suggestion_body(query, field_value = "content.trigram", slop_value = 3, field_name_value = "content")
				phsug_tags = get_suggestion_body(query, field_value = "tags.trigram", slop_value = 2, field_name_value = "tags")

				queryNameInfo = [0, 0.0, "", ""] #[queryNameInfo[0],queryNameInfo[1],queryNameInfo[2],query_display_name]
				queryContentInfo = [0, 0.0, "", ""]
				queryTagsInfo = [0, 0.0, "", ""]

				dqlis = [] 			# a list containing all the text inserted within double quotes
				q = "" 				# a string to hold the text not enclosed within ""

				#including quotes
				if('"' in query):
					l = re.split('(")', query) # this will split the query into tokens where delemiter is " and the delimiter is itself a token 
					qlist = list(filter(lambda a: a!='', l))
					
					itr = 0
					while(itr<len(qlist)):
						if(qlist[itr]=='"'):
							if(itr+2<len(qlist) and qlist[itr+2]=='"'):
								dqlis.append(qlist[itr+1])
								itr+=2
						else:
							q += qlist[itr]
						itr += 1

				print(dqlis, q)

				#dealing with the case when the user has given "" in the query
				if(len(dqlis)>0):
					query_body = '{ "query": {"bool": { "should": ['
					for quot in dqlis:
						query_body += ('{"multi_match": {"query": "%s", "fields": ["name^3", "altnames", "content^2", "tags"], "type": "phrase"}},' % (quot))
					if(q!=''):
						query_body += ('{"multi_match": {"query": "%s", "fields": ["name^3", "altnames", "content^2", "tags"], "type": "best_fields"}},' % (q))
					query_body += (']}}, "from": 0, "size": 100}')
					query_body = eval(query_body)	
					query_display = query

				else:

					get_suggestion(phsug_name, queryNameInfo, select, query, "name")
					if(queryNameInfo[2]!=query):
						get_suggestion(phsug_content, queryContentInfo, select, query, "content")
					if(queryNameInfo[2]!=query and queryContentInfo[2]!=query):
						get_suggestion(phsug_tags, queryTagsInfo, select, query, "tags")

					print (queryNameInfo[0],queryContentInfo[0],queryTagsInfo[0])
					query_display = ""

					altinfo_list = []
					#what if all are 1 and 2/3 names are same but the third one has higher score
					if((queryNameInfo[0]==1 and queryNameInfo[2]==query) or (queryContentInfo[0]==1 and queryContentInfo[2]==query) or (queryTagsInfo[0]==1 and queryTagsInfo[2]==query)): 
						#if the original query is the query to be searched
						query_display = query
					elif(queryNameInfo[0]==0 and queryContentInfo[0]==0 and queryTagsInfo[0]==0):																		
						#if we didnt find any suggestion, neither did we find the query already indexed->query remains same
						query_display = query
					else: #if we found a suggestion 
						altinfo_list = ["<h3>No results found for <b>%s</b></h3>" % (query)]
						res1_list = ['Search instead for <a href="">%s</a>'%(query)] #if the user still wants to search for the original query he asked for
						if(queryNameInfo[1]>=queryContentInfo[1] and queryNameInfo[1]>=queryTagsInfo[1]):						 #comparing the scores of name,content,tags suggestions and finding the max of the three
							query = queryNameInfo[2]
							query_display = queryNameInfo[3]					 #what query to display on the search result screen
						if(queryContentInfo[1]>queryNameInfo[1] and queryContentInfo[1]>=queryTagsInfo[1]):
							query = queryContentInfo[2]
							query_display = queryContentInfo[3]
						if(queryTagsInfo[1]>queryContentInfo[1] and queryTagsInfo[1]>queryNameInfo[1]):
							query = queryTagsInfo[2]
							query_display = queryTagsInfo[3]
						
						#if(es.search(index=GSTUDIO_SITE_NAME, doc_type=select, body=query_body)['hits']['total']>0):
						altinfo_list.append("<h3>Showing results for <b>%s</b></h3>" % query_display)


					if(queryNameInfo[0]==0 and queryContentInfo[0]==0 and queryTagsInfo[0]==0):#if we didnt find any suggestion, neither did we find the query already indexed
						query_body = {"query": {
											"multi_match": { 											#first do a multi_match
												"query" : query,
												"type": "best_fields",									#when multiple words are there in the query, try to search for those words in a single field
												"fields": ["name^3", "altnames", "content^2", "tags"],	#in which field to search the query
												"minimum_should_match": "30%"
												}
											},
										"rescore": {													#rescoring the top 50 results of multi_match
											"window_size": 50,
											"query": {
												"rescore_query": {
													"bool": {											#rescoring using match phrase
														"should": [
															{"match_phrase": {"name": { "query": query, "slop":2}}},
															{"match_phrase": {"altnames": { "query": query, "slop": 2}}},
															{"match_phrase": {"content": { "query": query, "slop": 4}}}
														]
													}
												}
											}
										},
										"from": 0,
										"size": 100
									}

					else: #if we found a suggestion or if the query exists as a phrase in one of the name/content/tags field
						query_body = {"query": {
											"multi_match": {
												"query": query,
												"fields": ["name^3", "altnames", "content^2", "tags"],
												"type": "phrase", #we are doing a match phrase on multi field.
												"slop": 5
											}
										},
										"from": 0,
										"size": 100
									}

					# query_display = query

				resultSet = search_query(GSTUDIO_SITE_NAME, select, group, query_body)
				hits = "<h3>No of docs found: <b>%d</b></h3>" % len(resultSet)
				if(group=="All"):
					res_list = ['<h3>Showing results for <b>%s</b> :</h3' % query_display, hits]
				else:
					res_list = ['<h3>Showing results for <b>%s</b> in group <b>"%s"</b>:</h3>' % (query_display, group), hits]
				med_list = get_search_results(resultSet)
				if(len(altinfo_list)>0):
					res_list = [hits]
				
		paginator = Paginator(med_list, GSTUDIO_NO_OF_OBJS_PP)
		page = request.GET.get('page')
		print(page)
		try:
			results = paginator.page(page)
		except PageNotAnInteger:
			results = paginator.page(1)
		except EmptyPage:
			results = paginator.page(paginator.num_pages)
		return render(request, 'ndf/sform.html', {'form': form, 'grpnam': group, 'grp': GROUP_CHOICES, 'header':res_list, 'alternate': altinfo_list ,'content': results, 'append_to_url':append_to_url})
	return render(request, 'ndf/sform.html', {'form': form, 'grp': GROUP_CHOICES})
	

def get_suggestion_body(query, field_value, slop_value, field_name_value):
	phrase_suggest = {												#json body of phrase suggestion in name field
		"suggest": {
			"text": query,										#the query for which we want to find suggestion
				"phrase": {											
					"field": field_value,					#in which indexed field to find the suggestion
					"gram_size": 3,								#this is the max shingle size
					"max_errors": 2,							#the maximum number of terms that can be misspelt in the query
					"direct_generator": [ {
			          "field": field_value,
			          #"suggest_mode": "missing",
			          "min_word_length": 2,
					  "prefix_length": 0,						#misspelling in a single word may exist in the first letter itself
			          "suggest_mode":"missing"					#search for suggestions only if the query isnt present in the index
			        } ],
			        "highlight": {								#to highlight the suggested word
			          "pre_tag": "<em>",
			          "post_tag": "</em>"
			        },
			        "collate": {								#this is used to check if the returned suggestion exists in the index
			        	"query": {
			        		"inline": {
			        			"match_phrase": {				#matching the returned suggestions with the existing index
			        				"{{field_name}}": {
				        				"query": "{{suggestion}}",
				        				"slop": slop_value					
				        			}
			        			}
			        		}
			        	},
			        	"params": {"field_name": field_name_value},
			        	"prune": True							#to enable collate_match of suggestions
			        }
				},
			}
		}
	return phrase_suggest

def get_suggestion(suggestion_body, queryInfo, doc_types, query, field):
	res = es.suggest(body=suggestion_body, index=GSTUDIO_SITE_NAME)						#first we search for suggestion in the name field as it has the highest priority																				
	if(len(res['suggest'][0]['options'])>0):									#if we get a suggestion means the phrase doesnt exist in the index
		for sugitem in res['suggest'][0]['options']:
			if sugitem['collate_match'] == True:								#we find the suggestion with collate_match = True
				queryInfo[0] = 1
				queryInfo[1] = sugitem['score']
				queryInfo[2] = sugitem['text']				
				queryInfo[3] = sugitem['highlighted']						#the query to be displayed onto the search results screen
				break
	else:						#should slop be included in the search part here?
		query_body = {"query":{"match_phrase":{field: query,}}}
		if(es.search(index=GSTUDIO_SITE_NAME, doc_type=doc_types, body=query_body)['hits']['total']>0):
			queryInfo[0] = 1							#set queryNameInfo[0] = 1 when we found a suggestion or we found a hit in the indexed data
			queryInfo[2] = query


def get_search_results(resultArray):
	reslist = [doc['_source'] for doc in resultArray]
	return reslist

def resources_in_group(res,group):
	results = []
	group_id = group_map[group]
	print group_id
	for i in res["hits"]["hits"]:
		if "group_set" in i["_source"].keys():
			k = []
			for g_id in (i["_source"]["group_set"]):
				k.append(g_id["$oid"]) 
			if group_id in k:
				results.append(i)
	return results

def search_query(index_name, select, group, query):
	siz = 100
	if(index_name == author_index):
		try:
			doctype = author_map[str(query)]
		except:
			return []
		else:
			body = {
						"query":{
							"match_all":{}
						},
						"from": 0,
						"size": siz
					} 

	elif(index_name == GSTUDIO_SITE_NAME):
		doctype = select
		body = query

	elif(index_name == gsystemtype_index):
		body = query
		doctype = select
	
	resultSet = []
	temp = []
	i = 0
	
	while(True):
		body['from'] = i
		res = es.search(index = index_name, doc_type=doctype, body = body)
		l = len(res["hits"]["hits"])
		print (body)
		if(l==0):
			return []
		if l > 0 and l <= siz:
			if(group == "All"):
				resultSet.extend(res["hits"]["hits"])
			else:
				temp = resources_in_group(res,group)
				resultSet.extend(temp)
			if l < siz:
				break		
			i+=siz	

	return resultSet


def get_advanced_search_form(request):
	with open(mapping_directory+"/gsystemtype_map.json") as gm:
		gsystemtype_map = json.load(gm)

	with open(mapping_directory+"/attribute_map.json") as am:
		attribute_map = json.load(am)

	with open(mapping_directory+"/relation_map.json") as rm:
		relation_map = json.load(rm)

	gsystemtype_map_str = json.dumps(gsystemtype_map)
	attribute_map_str = json.dumps(attribute_map)
	relation_map_str = json.dumps(relation_map)
	return render(request, 'ndf/advanced_search.html',{"gsystemtype_map":gsystemtype_map_str,'attribute_map':attribute_map_str,'relation_map':relation_map_str})

def advanced_search(request):
	node_type = request.GET.get("node_type")
	arr_attributes = json.loads(request.GET["arr_attributes"])
	arr_relations = json.loads(request.GET["arr_relations"])

	query_body = ""
	if(len(arr_attributes)>0 or len(arr_relations)>0):
		query_body = '{ "query": {"bool": { "must": ['
	for attr_name, atr_value in arr_attributes.iteritems():
		query_body += ('{"match": { "%s": "%s"}},' % (attr_name, atr_value))
	for rel_name, rel_value in arr_relations.iteritems():
		query_body += ('{"match": { "%s": "%s" }},' % (rel_name, rel_value))
	query_body += (']}}, "from": 0, "size": 100}')
	query_body = eval(query_body)

	res = search_query(gsystemtype_index, node_type, "All", query_body)
	med_list = get_search_results(res)
	print len(med_list)
	return HttpResponse(json.dumps({"results": med_list}), content_type="application/json")