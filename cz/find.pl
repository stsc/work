#!/usr/bin/perl
#===============================
# Finde HTML Links im CZ-Prozess
#===============================
# Benutzung:
# °°°°°°°°°°
# Das Script muss über die Powershell-Konsole via
# installiertem Perl-Interpreter aufgerufen werden.
# Mögliche Aufrufoptionen sind über die Hilfe Ausgabe
# (perl .\find.pl --help) oder Dokumentation einsehbar.
# -----------------------------------------------------
# Version: v0.05 - 2020-11-13 / ssc
# ---------------------------------

use strict;
use warnings;
use open qw(:std :utf8);
use constant true  => 1;
use constant false => 0;

use File::Find;
use File::Spec;
use Getopt::Long qw(:config no_auto_abbrev no_ignore_case);
use HTML::LinkExtor;
use LWP::UserAgent;
#use Win32::Console;

my $VERSION = '0.05';

my $Exclude_file = 'exclude.txt';

qx(chcp 65001 2>&1); # UTF-8, discard STDOUT
#my $CONSOLE = Win32::Console->new;
#my $codepage_orig = $CONSOLE->OutputCP;
#$CONSOLE->OutputCP(65001); # UTF-8

usage(0) unless @ARGV;

my %opts;
GetOptions(\%opts, qw(abs_prefix=s absolute broken extension=s h|help relative slashes summary V|version)) or usage(1);
usage(0) if $opts{h};

print "$0 v$VERSION\n" and exit 0 if $opts{V};

die "$0: --absolute and --relative are mutually exclusive\n" if $opts{absolute} && $opts{relative};

die "$0: --abs_prefix arg must be file|http|https\n" if defined $opts{abs_prefix} && $opts{abs_prefix} !~ /^(?:file|https?)$/;

my $abs_prefix = defined $opts{abs_prefix} ? qr{^(?:$opts{abs_prefix})://} : qr{^(?:file|https?)://};

my $seen_link = false;
my @links;

my ($count_files, $count_links) = (0) x 2;

my @exclusions;
if (-e $Exclude_file) {
    open(my $fh, '<', $Exclude_file) or die "Cannot open $Exclude_file for reading: $!\n";
    chomp(@exclusions = <$fh>);
    close($fh);
}

my $p = HTML::LinkExtor->new(\&callback);

foreach my $directory (@ARGV) {
    find({ preprocess => sub { return sort @_ }, wanted => \&wanted, no_chdir => true }, $directory);
}

print <<"EOT" if $opts{summary};
Total $count_files files.
Total $count_links links.
EOT

#$CONSOLE->OutputCP($codepage_orig);

sub usage
{
    my ($exit_code) = @_;

    print <<"USAGE";
Usage: $0 <directories to traverse> [switches]
        --abs_prefix=<prefix>    absolute prefix, defaults to: (file|http|https)
        --absolute               list absolute links
        --broken                 list broken links only
        --extension=<ext>        extract links with extension
    -h, --help                   this help screen
        --relative               list relative links
        --slashes                list links with slashes only
        --summary                print summary
    -V, --version                print version
USAGE
    exit $exit_code;
}

sub do_print(@)
{
    print @_ unless $opts{summary};
}

sub callback
{
    my ($tag, %links) = @_;

    return unless $tag eq 'area' && exists $links{href};

    return if $links{href} =~ /^#/;
    return if $links{href} =~ /^(?:javascript|mailto):/;

    foreach my $exclude (@exclusions) {
        next if $exclude =~ /^#/;
        return if $links{href} =~ /\Q$exclude\E/;
    }

    return if defined $opts{extension} && $links{href} !~ /\.\Q$opts{extension}\E$/;

    return if $opts{absolute} && $links{href} !~ $abs_prefix;
    return if $opts{relative} && $links{href} =~ $abs_prefix;

    my $extract_link = sub
    {
        my ($link, $links) = @_;
        $$link = $links->{href} =~ m{$abs_prefix/?(.*)$}
          ? $1
          : File::Spec->catfile($File::Find::dir, $links->{href});
        return false unless defined $$link && length $$link;
        return true;
    };

    if ($opts{slashes}) {
        my $link;
        return unless $extract_link->(\$link, \%links);
        my $path = $links{href} =~ $abs_prefix ? $link : $links{href};
        return if $path !~ m{/};
    }

    if ($opts{broken}) {
        if ($links{href} =~ m{^https?://}) {
            return unless LWP::UserAgent->new->head($links{href})->is_error;
        }
        else {
            my $link;
            return unless $extract_link->(\$link, \%links);
            return if -e $link;
        }
    }

    push @links, $links{href};

    $count_links++;
    $seen_link ||= true;
}

sub wanted
{
    return unless /\.html?$/;

    $seen_link = false;
    @links = ();

    $p->parse_file($File::Find::name);

    if ($seen_link) {
        my $title = "HTML File: $File::Find::name";
        do_print $title, "\n";
        do_print '=' x length $title, "\n";

        do_print "Link: $_\n" foreach @links;
        do_print "\n";

        $count_files++;
    }
}
