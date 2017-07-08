#!/usr/bin/perl -w

my ($cntA,$cntB,$file) = (0,0);
opendir(DIR,".");
while(defined($file = readdir(DIR))){
   if($file =~ /^\./){ next;}
   if($file =~ /\.pl/){ next;}
   my $tmp = `perl count.pl < $file`;
   my ($a,$c) = split(/\s+/,$tmp);
   $cntA += $a; $cntB += $c;
}
closedir(DIR);
print "COUNT: $cntA $cntB\n";
