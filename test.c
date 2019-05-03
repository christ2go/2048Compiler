int nr(int v) {
    return v*v;
}

int main() {
    int t = nr(4);
}

int check(short* feld, int y) {
      if(feld[0] == 2048)
        return 1;

  return 0;
}

int place(short* feld, int l, int p, int s) {
    if(feld[p] == 0)
    {
        feld[p] = s;
        return 0;
    }
    return 1;
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