#include<stdio.h>
#include<cs50.h>

int main(void)
{
int height;
do
 {
  //get height from user
 printf("give me the height:\n");
 height=get_int();
 }
 while(height<0 || height>23);


 int row;
{
 for(row=0;row<height;row++)
 {
   for(int space=height-1;space>row;space--)
      {
       //space
       printf(" ");
      }
    for(int hashes=0;hashes<=row+1;hashes++)
      {
       //hashes
         printf("#");
      }
 printf("\n");
 }
}
}
