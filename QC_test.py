from qcmanager.QC_help import iqa, object_count, duplicates

image_path = ['images'] #[args.path]

if __name__ == '__main__':

   #IQA
   iqa_ = iqa(image_path)
   #Object count
   object_count_ = object_count(image_path)
   #Remove Duplicates
   duplicate_ = duplicates(image_path)
   
   print("***********iqa results***********")
   print(iqa_)
   print("*********************************")

   print("***********oc results***********")
   print(object_count_)
   print("*********************************")

   print("********duplicate results********")
   print(duplicate_)
   print("*********************************")
   
