#!/usr/bin/perl -w

my ($on,$countA,$countB,$line) = (0,0,0);
while(defined($line = <STDIN>)){
   if($line =~ /;Node/){
	$on = 1;
   }
   elsif($line =~ /;Edge/){
      last;
   }
   elsif($line =~ /^\d/){
      my ($a) = split(/\s+/,$line);
      if($a == 0){ $countA++;}
      else       { $countB++;}
   }
}

print "$countA $countB\n";
