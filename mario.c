#include<stdio.h>
#include<cs50.h>

int main(void)
{
int height;
do
 {
  //get height from user
 //printf();
 height=get_int("give me the height:\n");
 }
 while(height<1 || height>8);


 int row;
{
 for(row=0;row<height;row++)
 {
   for(int space=height-1;space>row;space--)
      {
       //space
       printf(" ");
      }
    for(int hashes=1;hashes<=row+1;hashes++)
      {
       //hashes
         printf("#");
      }
 printf("\n");
 }
}
}
