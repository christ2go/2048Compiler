int check(short* feld, int y) {
  for(int i = 0; i < y; i = i+1) {
    for(int j = 0; j < y; j = i+1) {
      if(feld[y*i+j] == 2048)
        return 1;
    }
  }
  return 0;
}


int set(short* feld, int l, int p, int s) {
    feld[p] = s;
  }



int move_one(short** feld, int l) {
  int set = 0;
  for(int i = 0; i < l;i = i+1) {
    if(i < (l-1) && *feld[i] == 0) {
      *feld[i] = *feld[i+1];
      *feld[i+1] = 0;
      set = 1;
    }
  }
  return set;
}



void rotateMatrix(int *mat, int N)
{
    for (int x = 0; x < N / 2; x = x+1)
    {
        for (int y = x; y < N-x-1; y = y+1)
        {
            int temp;
             temp = mat[x*N+y];

            mat[x*N+y] = mat[y*N+N-1-x];

            mat[y*N+N-1-x] = mat[(N-1-x)*N+N-1-y];

            mat[(N-1-x)*N+N-1-y] = mat[(N-1-y)*N+x];

            mat[(N-1-y)*N+x] = temp;
        }
    }
}


