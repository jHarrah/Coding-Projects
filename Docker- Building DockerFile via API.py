"""
Code created by Justin Harrah 
For: APSU GIS Center 
Project: Veteran Reconnect Grant- Dockerizing
Date: Feb 2019 
"""



import docker
import sys
 

""" 
Outline: 
      ListContainter; 
      List active containers 

      Build DockerFile: 
      find and remove existing image 
      rebuild image from DockerFile in current directory 

      Reset: 
      find and stop vet reconnect grant container if running 
      remove vet reconnect container 
      Prompt user for intended container volume location
      rebuild and deploy container using new docker file 



PRERUN requirements: 
This package requires the Docker tools for Python. Documentation can be found in below link. 
https://pypi.org/project/docker/
 """ 
client = docker.from_env() 

def main():
      listContainers()
      BuildDockerFile()
      Reset()
      print("Operation completed")
      return 0
    
 
def listContainers(): 
      
      print("Container ID(S):")
      """ Code in the below section will output a list of running containers"""
      for container in client.containers.list(): 
            print (container.id)
      
      print ("\n")
      return 0

def BuildDockerFile():
      print(" Building DockerFile from current director...") 
      "The below line will remove existing docker images for vet reconnect" 
      try: 
            client.images.get('vet_reconnect_docker')      
            client.images.remove('vet_reconnect_docker')
            print(" Veteran Reconnect image was found and successfully removed.")
            
      except docker.errors.ImageNotFound: 
            print(" Veteran Reconnect image was not found.")
      except docker.errors.APIError: 
            print(" An unexpected error has occured while searching for the Veteran Reconnect image.")

      try:
            client.images.build(path = "./", tag = 'vet_reconnect_docker')
      except docker.errors.BuildError: 
            print(" Error: Dockerfile was not found in the current directory. Exiting! ")
            sys.exit(0)
      except docker.errors.APIError: 
            print(" Error: An unexpected Python API error has occured and the program is not able to continue. Exiting! ")
            sys.exit(0)
            
      print (" An updated image has been successfully created.")
      print ("\n")
      return 0 




def Reset():
      'The run shell script is represented within the below lines'
      print(" Attempting to stop Vetern Reconnect Grant container")

      """ Creates an array and places each present container name into an element"""
      try:
            vrg=client.containers.get('vet_reconnect_grant')
            vrg.stop()
            vrg.remove()
            print(" Container has stopped.")  
      except: 
            print(" Container vet_reconnect_grant not found")   

               
      LocalVolumePath=input(" Please enter the desired volume path on the next line. If no input is provided the current directory will be selected.\n")
      '''
         This block is intended to verify input
         Note: isinstance() will return true if localvolumepath contains a string or false if not
      ''' 
      while isinstance(LocalVolumePath,str) == False and LocalVolumePath != None:
            print(" You have entered an invalid path.")
            LocalVolumePath=input(" Please enter the desired volume path on the next line.The current directory will be used if nothing is entered.\n")
            
        
      '''Double // is required to  ensure the path is in the correct path for docker volume command formate'''
      if LocalVolumePath is None: 
            LocalVolumePath= '//./' 
      else: 
            pass1="//" + LocalVolumePath 
            pass2=pass1.replace(':',"") 
            LocalVolumePath=pass2



      print (" You have selected %s as the container volume location" %LocalVolumePath)
      
      try:
            "This step will start a new container using the image built in the BuildDockerFile function"
            client.containers.run('vet_reconnect_docker',name='vet_reconnect_grant', detach=True, volumes=({LocalVolumePath: {'bind': r'/var/www/html','mode': 'ro'}}), ports={'80/tcp': 33080})
      except docker.errors.ContainerError: 
            print(" The container (while detached) has experienced an error that resulted in a non-zero value on exit. Exiting!!")
            sys.exit()
      except docker.errors.ImageNotFound : 
            print(" The designated image file was not found, resulting in an error. Exiting!!")
            sys.exit()
      except docker.errors.APIError:
            print(" A nondescript error related to the Docker API has occured.Exiting!! ")

      print('A new container has been started using name "vet_reconnect_grant" ')
      return 0

main()


""" Look into using os.path.exists() to validate user path selction
    https://docs.python.org/2/library/os.path.html
    

   volumes=({'//c/users/justin/Desktop/GIS_Stuff': {'bind': r'/var/www/html','mode': 'ro'}}))
"""