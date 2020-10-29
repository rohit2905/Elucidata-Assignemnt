from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import pandas as pd 
from zipfile import ZipFile
import os
import io

from .forms import FileUpload


#For uploading the file
def upload(request):
	if request.method == 'POST':
		upload_form = FileUpload(request.POST,request.FILES)
		if upload_form.is_valid():
			f = request.FILES['upload_file']
			filename = str(f)
			with open('uploaded_file/'+filename,'wb+') as out:
				for data in f:
					out.write(data)
			response = HttpResponse("Upload Success")		
			return HttpResponseRedirect( '/'+filename+'/operation1')  #upon succesfull uploading
	else:	
		upload_form = FileUpload()									#failed upload
	return render(request,'index.html',{'form':upload_form})	



#API for the 1st set of operations
def operation1(request,filename):
	df = pd.read_excel('uploaded_file/'+filename)
	extra_file = operation2(request,filename)
	#print(extra_file)
	extra_file.to_csv('Rounded_Retention_Time.csv', index=True)
	pc_df = df[(df['Accepted Compound ID'].str.endswith('PC',na=False)) & (df['Accepted Compound ID'].str[-3]!='L')]

	pc_df.to_csv('PC.csv',index=False)

	lpc_df = df[df['Accepted Compound ID'].str.endswith('LPC',na=False)]
	lpc_df.to_csv('LPC.csv',index=False)


	plasgn_df = df[df['Accepted Compound ID'].str.endswith('plasmalogen',na=False)]
	plasgn_df.to_csv('Plasmalogen.csv',index=False)

	zip_file_list = ['PC.csv','LPC.csv','Plasmalogen.csv','Rounded_Retention_Time.csv']
	
	download_file = io.BytesIO()
	with ZipFile(download_file,'w') as zip_file:
		for csv_file in zip_file_list:
			zip_file.write(csv_file)
			os.remove(csv_file) 

	response = HttpResponse(download_file.getvalue(),content_type='application/octet-stream')		
	response['Content-Disposition'] = 'attachment; filename="output.zip"'
			
	return response


def rounded_time(row):
	time = row['Retention time (min)'] 
	if time>1:
		return round(time)
	else:
		return 1	
def operation2(request,filename):
	df = pd.read_excel('uploaded_file/'+filename)

	rounded_retention_time = df.apply(lambda row : rounded_time(row),axis=1)
	df.insert(2,'Retention Time Roundoff (in mins)',rounded_retention_time)


	del df['m/z']
	del df['Retention time (min)']

	new_df = df.groupby(df['Retention Time Roundoff (in mins)']).mean()

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Rounded_Retention_Time.csv"'

	new_df.to_csv(response,index=True)

	return new_df






