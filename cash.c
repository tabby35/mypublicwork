#include<stdio.h>
#include<cs50.h>
#include<math.h>

int main(void)
{
  float change=0;
    do
    {
        //printf();
        change=get_float("how much $ owed?\n");
    }
   while(change<0);
    int amount=round(change*100);

    int quart,dime,nickle,penny;
    quart=amount/25;

    amount=amount%25;

    dime=amount/10;

    amount=amount%10;

    nickle=amount/5;

    amount=amount%5;

    penny=amount;

    printf("%d\n",quart+dime+nickle+penny);
}