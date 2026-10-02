#include <stdio.h>
#include <stdbool.h>

#define MAX_LOT_LENGTH 9
#define MAX_CAR_AMOUNT 10

#define EMPTY_SLOT ' '
#define EMPTY_SLOT_INPUT 'x'
#define RED_CAR_CHAR '*'

#define MAX_TURN_COUNT 10

int inputAndParseParkingLot(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH]){
    printf("Are you ready for rush hour?\n");
    int length = -1;
    printf("Please enter the parking lot length: ");
    scanf("%d", &length); // assume this is always correct
    printf("Please enter the parking lot:\n");
    for(int i =0; i < length; ++i){
        for(int j = 0; j < length; ++j){
            scanf(" %c", &(lot[i][j]));
            if(lot[i][j] == EMPTY_SLOT_INPUT){
                lot[i][j] = EMPTY_SLOT;
            }
        }
    }
    return length;
}

void printParkingLot(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length){
    for(int k = 0; k < length; ++k){
            printf("~~~");
        }
    printf("\n");
    for(int i = 0; i < length; ++i){
        for(int j = 0; j < length; ++j){
            printf("|%c|", lot[i][j]);
        }
        printf("\n");
        for(int k = 0; k < length; ++k){
            printf("~~~");
        }
        printf("\n");
    }
}

void printEnterCar(){
    printf("Enter the car you want to move:\n");
}

void printInvalidCar(){
    printf("Invalid car id! enter again:\n");
}

void printEnterDirection(){
    printf("Please enter the direction to move the car:\n");
}

void printInvalidDirection(){
    printf("Invalid direction!\n");
}

void printInvalidMove(){
    printf("Invalid move!\n");
}

void printGameWon(){
    printf("GAME OVER! YOU WIN :D\n");
}

void printGameLost(){
    printf("GAME OVER! YOU LOST :(\n");
}

bool check_right(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){
if (lot[i][j]==lot[i][j+1])
    return true;
else
    return false;
}
bool check_left(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){
if (lot[i][j]==lot[i][j-1])
    return true;
else
    return false;
}
bool check_up(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){
if (lot[i][j]==lot[i-1][j])
    return true;
else
    return false;
}
bool check_down(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){
if (lot[i][j]==lot[i+1][j])
    return true;
else
    return false;
}

int up_left_corner (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool r=check_right(lot,length,i,j);
bool d=check_down(lot,length,i,j);

if (d && r)
return 3; //riboeit

if (r)
return 1;// ----->

if (d)
return 2;//------^
}

int up_right_corner (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool l=check_left(lot,length,i,j);
bool d=check_down(lot,length,i,j);

if (d && l)
return 3; //riboeit

if (l)
return 1;// ----->

if (d)
return 2;//------^
}

int down_right_corner (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool l=check_left(lot,length,i,j);
bool u=check_up(lot,length,i,j);

if (l && u)
return 3; //riboeit

if (l)
return 1;// ----->

if (u)
return 2;//------^
}

int down_left_corner (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool r=check_right(lot,length,i,j);
bool u=check_up(lot,length,i,j);

if (u && r)
return 3; //riboeit

if (r)
return 1;// ----->

if (u)
return 2;//------^
}

int left_row (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool r=check_right(lot,length,i,j);
bool u=check_up(lot,length,i,j);
bool d=check_down(lot,length,i,j);

if ((d||u) && r)
return 3; //riboeit

if (r)
return 1;// ----->

if (d||u)
return 2;//------^
}

int right_row (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool l=check_left(lot,length,i,j);
bool u=check_up(lot,length,i,j);
bool d=check_down(lot,length,i,j);

if ((d||u) && l)
return 3; //riboeit

if (l)
return 1;// ----->

if (d||u)
return 2;//------^
}

int up_line (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool l=check_left(lot,length,i,j);
bool r=check_right(lot,length,i,j);
bool d=check_down(lot,length,i,j);

if ((l||r) && d)
return 3; //riboeit

if (l||r)
return 1;// ----->

if (d)
return 2;//------^
}

int low_line (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool l=check_left(lot,length,i,j);
bool r=check_right(lot,length,i,j);
bool u=check_up(lot,length,i,j);

if ((l||r) && u)
return 3; //riboeit

if (l||r)
return 1;// ----->

if (u)
return 2;//------^
}

int middle_board (char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length,int i,int j){

bool l=check_left(lot,length,i,j);
bool r=check_right(lot,length,i,j);
bool u=check_up(lot,length,i,j);
bool d=check_down(lot,length,i,j);

if ((l||r) && (u||d))
return 3; //riboeit

if (l||r)
return 1;// ----->

if (u||d)
return 2;//------^
}

int ascii_converter(char c){
    int num;
    switch(c){
    case '1':{
    num=1;
    break;}
    case '2':{
    num=2;
    break;}
    case '3':{
    num=3;
    break;}
    case '4':{
    num=4;
    break;}
    case '5':{
    num=5;
    break;}
    case '6':{
    num=6;
    break;}
    case '7':{
    num=7;
    break;}
    case '8':{
    num=8;
    break;}
    case '9':{
    num=9;
    break;}
    default:{
    num=-1;
    break;}
    }
return num;
}

int cartype(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car){
for (int i=0;i<length;i++){
    for (int j=0;j<length;j++){
        if (lot[i][j]== car){

           if (i==0 && j==0){
            return (up_left_corner(lot,length,i,j));
           }
           if (i==length-1 && j==0){
            return (down_left_corner(lot,length,i,j));
           }
           if (i==0 && j==length-1){
            return (up_right_corner(lot,length,i,j));
           }
           if (i==length-1 && j==length-1){
            return (down_right_corner(lot,length,i,j));
           }
           if (i==0){
            return (up_line(lot,length,i,j));
           }
            if (i==length-1){
            return (low_line(lot,length,i,j));
           }
           if (j==0){
            return (left_row(lot, length,i,j));
           }
           if (j==length-1){
            return (right_row(lot,length,i,j));
           }
            return (middle_board(lot, length,i,j));
        }
    }
}
}

int car_num_total(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH],int length){
int max=0;
int num;
char c;
for (int i=0;i<length;i++){
    for (int j=0;j<length;j++){
    c=lot[i][j];
    num=ascii_converter(c);
if (num>max)
max=num;
}}
return max;
}

char get_direction(){

printEnterDirection();

char direction;

scanf(" %c", &direction);

if (direction!= 'r' && direction!= 'l' && direction!= 'd' && direction!= 'u'){
    printInvalidDirection();
    return 'x';
}
return  direction;
}

char get_car(int car_num_total){

    char car;

    printEnterCar();

    scanf(" %c", &car);

    int current_car=ascii_converter(car);

    while (car!='*' && (current_car>car_num_total || current_car==-1)){
        printInvalidCar();
        scanf(" %c", &car);
        current_car=ascii_converter(car);
        }

    return car;
}



void move_car_right(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int l, int r, int line){
lot[line][r+1]= lot[line][l];
lot[line][l]= EMPTY_SLOT;
return;
}
void move_car_left(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int l, int r, int line){
lot[line][l-1]= lot[line][r];
lot[line][r]= EMPTY_SLOT;
return;
}
void move_car_up(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int u, int d, int row){
lot[u-1][row]= lot[d][row];
lot[d][row]= EMPTY_SLOT;
return;
}
void move_car_down(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int u, int d, int row){
lot[d+1][row]= lot[u][row];
lot[u][row]= EMPTY_SLOT;
return;
}





bool check_move_rl(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH],int length, int l, int r, int line, char direction){
    if (direction=='r' && r==length-1){
    printInvalidMove();
    return true;
}
if (direction=='l' && l==0){
    printInvalidMove();
    return true;
}
if (direction=='r' && lot[line][r+1]!= EMPTY_SLOT){
    printInvalidMove();
    return true;
}
if (direction=='l' && lot[line][l-1]!= EMPTY_SLOT){
    printInvalidMove();
    return true;
}
return false;
}
bool check_move_ud(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH],int length, int u, int d, int row, char direction){

if (direction=='u' && u==0){
    printInvalidMove();
    return true;
}
if (direction=='d' && d==length-1){
    printInvalidMove();
    return true;
}
if (direction=='u' && lot[u-1][row]!= EMPTY_SLOT){
    printInvalidMove();
    return true;
}
if (direction=='d' && lot[d+1][row]!= EMPTY_SLOT){
    printInvalidMove();
    return true;
}
return false;
}


int index_up(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car){
int i,j, row, d=0, u=length-1;
for (i=0;i<length;i++){
    for (j=0;j<length;j++){
        if (lot[i][j]==car){
        if (i<u)
        u=i;
        if (i>d)
        d=i;
        }
    }
}
return u;
}
int index_left(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car){
int i,j,r=0,l=length-1;
for (i=0;i<length;i++){
    for (j=0;j<length;j++){
        if (lot[i][j]==car){
        if (j<l)
        l=j;
        if (j>r)
        r=j;
        }
    }
}
return l;
}
int index_down(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car){

int i,j, row, d=0, u=length-1;
for (i=0;i<length;i++){
    for (j=0;j<length;j++){
        if (lot[i][j]==car){
        if (i<u)
        u=i;
        if (i>d)
        d=i;
        }
    }
}
return d;
}
int index_right(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car){
int i,j,r=0,l=length-1;
for (i=0;i<length;i++){
    for (j=0;j<length;j++){
        if (lot[i][j]==car){
        if (j<l)
        l=j;
        if (j>r)
        r=j;
        }
    }
}
return r;
}

void check_move_1(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car, int type, char direction){
int line,r,l;

if (direction!='r' && direction!='l'){
    printInvalidMove();
    return;
}

r= index_right(lot,length, car);
l= index_left(lot,length, car);
line= index_up(lot,length, car);


if (check_move_rl(lot,length,l,r,line,direction))
return;

if (direction=='r')
move_car_right(lot,l,r,line);

if (direction=='l')
move_car_left(lot,l,r,line);

return;
}

void check_move_2(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car, int type, char direction){
int row,d,u;

if (direction!='u' && direction!='d'){
    printInvalidMove();
    return;
}

row= index_right(lot,length, car);
d= index_down(lot,length, car);
u= index_up(lot,length, car);

if (check_move_ud(lot,length,u,d,row,direction))
return;

if (direction=='u')
move_car_up(lot,u,d,row);

if (direction=='d')
move_car_down(lot,u,d,row);

return;
}

void check_move_3(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car, int type, char direction){
int d,u,r,l,line,row;

r= index_right(lot,length, car);
l= index_left(lot,length, car);
u= index_up(lot,length, car);
d= index_down(lot,length, car);
row= index_right(lot,length, car);
line= index_up(lot,length, car);

if (check_move_ud(lot,length,u,d,row,direction))
return;

if (check_move_rl(lot,length,l,r,line,direction))
return;


if (direction=='u'){
move_car_up(lot,u,d,r);
move_car_up(lot,u,d,l);
}
if (direction=='d'){
move_car_down(lot,u,d,r);
move_car_down(lot,u,d,l);
}
if (direction=='r'){
move_car_right(lot,l,r,d);
move_car_right(lot,l,r,u);
}
if (direction=='l'){
move_car_left(lot,l,r,u);
move_car_left(lot,l,r,d);
}
return;
}

bool check_win(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length){
if (lot[length/2][length-1]== '*'){
printGameWon();
return true;
}
return false;
}

int move_car(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length, char car, int type, char direction){
if (type==1)
check_move_1(lot, length, car, type, direction);
if (type==2)
check_move_2(lot, length, car, type, direction);
if (type==3)
check_move_3(lot, length, car, type, direction);
}

void play(char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH], int length){
char car, direction;
int type;
int car_num = car_num_total(lot,length);


for (int turn=1 ; turn<11 ; turn++){

    printParkingLot(lot, length);

    if (check_win(lot, length))
    return;

    car = get_car(car_num);

    direction = get_direction();

    if (direction == 'x'){
    turn--;
    continue;
    }
    type = cartype(lot, length, car);
    move_car(lot, length, car, type, direction);
    }
    printParkingLot(lot, length);
    if (check_win(lot, length))
    return;

    printGameLost();
    return;
}

int main(){
    int length;
    char lot[MAX_LOT_LENGTH][MAX_LOT_LENGTH];
    length = inputAndParseParkingLot(lot);
    play(lot, length);
    return 0;
}

/*
1 1 x x x
1 1 2 2 2
* * 4 x x
x x 4 x x
x x 3 3 x
*/
