#include<bits/stdc++.h>
using namespace std;

int main()
{
	set<string> done,left;	
	freopen("restaurant_info_kolkata","r",stdin);
	freopen("restaurant_info_kolkata2","w",stdout);
	string s;
	int i;
	for(i=0;i<=3932;i++)
	{
		cin>>s;
		if(done.find(s)==done.end())
			{
				cout<<s<<endl;	
				done.insert(s);
			}			
		
	}
}
