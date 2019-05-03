int points;
int cval;

int check(short* feld, int y) {
  for(int i = 0; i < y; i++) {
    for(int j = 0; j < y; j++) {
      if(feld[y*i+j] == 2048)
        return 1;
    }
  }
  return 0;
}

int set(short* feld, int l, int p, int s) {
  if(feld[p] == 0)
  {
    feld[p] = s;
    return 1;
  }
  return 0;
}

int move_one(short** feld, int l) {
  int set = 0;
  for(int i = 0; i < l;i++) {
    if(i < (l-1) && *feld[i] == 0) {
      *feld[i] = *feld[i+1];
      *feld[i+1] = 0;
      set = 1;
    }
  }
  return set;
}

void move_left(short** feld,int l) {
  while(move_one(feld,l)) {

  }
}

