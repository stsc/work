#!/usr/bin/perl

use strict;
use warnings;
use constant true => 1;

use File::Find;

die "$0: <directory>\n" unless defined $ARGV[0] && -d $ARGV[0];

find({ wanted => \&wanted, no_chdir => true }, $ARGV[0]);

sub wanted
{
    return unless $File::Find::name =~ /\.html?$/;

    my $file = $File::Find::name;

    open(my $fh, '<', $file) or die "Cannot open `$file' for reading: $!";
    my $content = do { local $/; <$fh> };
    close($fh);

    return unless $content =~ /content="Fast Image-Map/;

    opendir(my $dh, $File::Find::dir) or die "Cannot open `$File::Find::dir' for reading: $!";
    my %image_maps = map { lc $_ => $_ } grep /\.jpg$/i, readdir($dh);
    closedir($dh);

    my $orig = $content;

    $content =~ s/(?<=^<img src=")([^"]+)(?=" .*? usemap=".*$)/$image_maps{$1} || $1/em;

    my $subst_sep = sub { local $_ = shift; s{\\}{/}g; $_ };
    $content =~ s/(?<=href=")([^"]+)(?=")/$subst_sep->($1)/eg;

    if ($content ne $orig) {
        open($fh, '>', $file) or die "Cannot open `$file' for writing: $!";
        print {$fh} $content;
        close($fh);

        print "Modified: $file\n";
    }
}
