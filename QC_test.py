from qcmanager.QC_help import IQA, ObjectCounter, duplicates

image_path_folder = ["images"] #[args.path]
image_path_list = ["images/1.png", "images/2.png", "images/3.png", "images/4.png", "images/8.png", "images/4 copy.png", "images/8 copy.png"] #[args.path]


if __name__ == "__main__":

   #IQA
   iqa = IQA()
   iqa_f = iqa.get_scores(image_path_folder)
   iqa_l = iqa.get_scores(image_path_list)

   #Object count
   oc = ObjectCounter()
   object_count_f = oc.object_count(image_path_folder)
   object_count_l = oc.object_count(image_path_list)
   
   # Remove Duplicates
   duplicate_f = duplicates(image_path_folder)
   duplicate_l = duplicates(image_path_list)
   
   print("***********iqa folder results***********")
   print(iqa_f)
   print("*********************************")

   print("***********iqa list results***********")
   print(iqa_l)
   print("*********************************")

   print("***********oc folder results***********")
   print(object_count_f)
   print("*********************************")

   print("***********oc list results***********")
   print(object_count_l)
   print("*********************************")

   print("********duplicate folder results********")
   print(duplicate_f)
   print("*********************************")
   
   print("********duplicate list results********")
   print(duplicate_l)
   print("*********************************")
