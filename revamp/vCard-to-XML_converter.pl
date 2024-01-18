#!/usr/bin/perl
#======================================
# Konvertiere vCard nach XML für Zoiper
#======================================
# Benutzung:
# °°°°°°°°°°
# Das Script muss über die Konsole via installiertem
# Perl-Interpreter aufgerufen werden. Mögliche Aufruf-
# optionen sind: --out=<output file> (Ausgabedatei).
#-----------------------------------------------------
# Version: v0.01 - 2023-12-07 / sts
#----------------------------------

use strict;
use warnings;
use utf8;
use constant true => 1;

use Getopt::Long qw(:config no_auto_abbrev no_ignore_case);
use List::MoreUtils qw(all);
use XML::Writer;

my %opts;
GetOptions(\%opts, 'out=s') or usage();

my (@in_files, $out_file);

if (@ARGV == 0) {
    usage();
}
else {
    $out_file = defined $opts{out} ? $opts{out} : undef;
    @in_files = @ARGV;
}

{
    my $writer = XML::Writer->new(OUTPUT => 'self', DATA_MODE => true, DATA_INDENT => 2, UNSAFE => true);

    $writer->xmlDecl('UTF-8');

    $writer->startTag('Contacts');

    my $id = 1;

    foreach my $in_file (@in_files) {
        open(my $fh, '<', $in_file) or die "Cannot open `$in_file': $!\n";
        my $vcf = do { local $/; <$fh> };
        close($fh);

        my @vcards;
        read_vcards($vcf, \@vcards);
        write_xml($writer, \@vcards, \$id);
    }

    $writer->endTag('Contacts');

    my $xml = $writer->end;

    if (defined $out_file) {
        open(my $fh, '>', $out_file) or die "Cannot open `$out_file': $!\n";
        print {$fh} $xml;
        close($fh);
    }
    else {
        print $xml;
    }
}

sub usage
{
    die "Usage: $0 <input file(s)> [--out=<output file>]\n";
}

sub read_vcards
{
    my ($vcf, $vcards) = @_;

    my @entries = $vcf =~ /(?<=^BEGIN:VCARD\r\n)(.+?)(?=^END:VCARD\r\n)/gms;

    foreach my $entry (@entries) {
        my %vcard;
        foreach my $line (split /\r\n/, $entry) {
            my ($left, $right) = split /:/, $line;
            my ($property, $parameter) = $left =~ /^(.+?)(?:\;(.+))?$/;
            my %hash;
            $hash{parameter} = $parameter;
            next unless defined $right;
            my ($attribute, $attributes) = $right =~ /^(.+?)(?:\;(.+))?$/;
            @hash{qw(attribute attributes)} = ($attribute, $attributes);
            push @{$vcard{$property}}, { %hash };
        }
        push @$vcards, { %vcard };
    }
}

sub write_xml
{
    my ($writer, $vcards, $id) = @_;

    my $write_phone = sub
    {
        my ($phone, $custom_type) = @_;

        $writer->startTag('Phone');

        $writer->startTag('Type');
        $writer->raw('Custom');
        $writer->endTag('Type');

        $writer->startTag('CustomType');
        $writer->raw($custom_type);
        $writer->endTag('CustomType');

        $writer->startTag('Phone');
        $writer->raw($phone->{attribute});
        $writer->endTag('Phone');

        $writer->startTag('Account');
        $writer->endTag('Account');

        $writer->startTag('Presence');
        $writer->endTag('Presence');

        $writer->startTag('AccountMappingType');
        $writer->endTag('AccountMappingType');

        $writer->startTag('PresenceMappingType');
        $writer->endTag('PresenceMappingType');

        $writer->endTag('Phone');
    };

    my $umlaut_to_unicode = sub
    {
        my ($string) = @_;

        my %table = (
            '&' =>  38,
            'Ä' => 196,
            'Ö' => 214,
            'Ü' => 220,
            'ä' => 228,
            'ö' => 246,
            'ü' => 252,
            'à' => 224,
            'è' => 232,
            'é' => 233,
        );
        foreach my $umlaut (keys %table) {
            $string =~ s/$umlaut/&#$table{$umlaut};/g;
        }

        return $string;
    };

    foreach my $vcard (@$vcards) {
        $writer->startTag('Contact', 'id' => $$id++);

        $writer->startTag('Name');

        $writer->startTag('First');
        $writer->endTag('First');

        $writer->startTag('Middle');
        $writer->endTag('Middle');

        $writer->startTag('Last');
        $writer->endTag('Last');

        my $full_name = $umlaut_to_unicode->($vcard->{FN}[0]{attribute});
        $writer->startTag('Display');
        $writer->raw("'$full_name'");
        $writer->endTag('Display');

        $writer->endTag('Name');

        $writer->startTag('Info');

        $writer->startTag('Company');
        $writer->endTag('Company');

        $writer->endTag('Info');

        foreach my $phone (@{$vcard->{TEL}}) {
            if (all { defined $phone->{$_} } qw(attribute parameter)) {
                next unless $phone->{parameter} =~ /^TYPE=(.+?)(?=\;|$)/;
                $write_phone->($phone, $1);
            }
        }

        $writer->startTag('Avatar');

        $writer->startTag('URL');
        $writer->endTag('URL');

        $writer->endTag('Avatar');

        $writer->endTag('Contact');
    }
}
