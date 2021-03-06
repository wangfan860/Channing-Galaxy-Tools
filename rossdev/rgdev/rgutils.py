# utilities for rgenetics 
# 
# copyright 2009 ross lazarus
# released under the LGPL
#

import subprocess, os, sys, time, tempfile

galhtmlprefix = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="Galaxy %s tool output - see http://g2.trac.bx.psu.edu/" />
<title></title>
<link rel="stylesheet" href="/static/style/base.css" type="text/css" />
</head>
<body>
<div class="document">
"""

galhtmlpostfix = """</div></body></html>\n"""

plinke = 'plink' # changed jan 2010 - all exes must be on path
rexe = 'R'       # to avoid cluster/platform dependencies
smartpca = 'smartpca.perl'

def timenow():
    """return current time as a string
    """
    return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(time.time()))

def fail( message ):
    print >> sys.stderr, message
    return -1

def whereis(program):
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, program)) and \
           not os.path.isdir(os.path.join(path, program)):
            return os.path.join(path, program)
    return None


def oRRun(rcmd=[],outdir=None,title='myR',rexe='R'):
    """
    run an r script, lines in rcmd,
    in a temporary directory
    move everything, r script and all back to outdir which will be an html file

    
      # test
      RRun(rcmd=['print("hello cruel world")','q()'],title='test')    
    """
    rlog = []
    print '### rexe = %s' % rexe
    assert os.path.isfile(rexe) 
    rname = '%s.R' % title
    stoname = '%s.R.log' % title
    rfname = rname
    stofname = stoname
    if outdir: # want a specific path
        rfname = os.path.join(outdir,rname)
        stofname = os.path.join(outdir,stoname)
        try:
        	os.makedirs(outdir) # might not be there yet...
        except:
            pass
    else:
        outdir = tempfile.mkdtemp(prefix=title)
        rfname = os.path.join(outdir,rname)
        stofname = os.path.join(outdir,stoname)
        rmoutdir = True
    f = open(rfname,'w')
    if type(rcmd) == type([]):
        f.write('\n'.join(rcmd))
    else: # string
        f.write(rcmd)
    f.write('\n')
    f.close()
    sto = file(stofname,'w')
    vcl = [rexe,"--vanilla --slave", '<', rfname ]
    x = subprocess.Popen(' '.join(vcl),shell=True,stderr=sto,stdout=sto,cwd=outdir)
    retval = x.wait()
    sto.close()
    rlog = file(stofname,'r').readlines()
    rlog.insert(0,'## found R at %s' % rexe)
    if outdir <> None:
        flist = os.listdir(outdir)
    else:
        flist = os.listdir('.')
    flist.sort
    flist = [(x,x) for x in flist] 
    for i,x in enumerate(flist):
        if x == rname:
            flist[i] = (x,'R script for %s' % title)
        elif x == stoname:
            flist[i] = (x,'R log for %s' % title)   
    if False and rmoutdir:
        os.rmdir(outdir)
    return rlog,flist # for html layout
            
            


def RRun(rcmd=[],outdir=None,title='myR'):
    """
    run an r script, lines in rcmd,
    in a temporary directory
    move everything, r script and all back to outdir which will be an html file

    
      # test
      RRun(rcmd=['print("hello cruel world")','q()'],title='test')   
    echo "a <- c(5, 5); b <- c(0.5, 0.5)" | cat - RScript.R | R --slave \ --vanilla 
    suggested by http://tolstoy.newcastle.edu.au/R/devel/05/09/2448.html
    """
    rlog = []
    rname = '%s.R' % title
    stoname = '%s.R.log' % title
    if outdir: # want a specific path
        try:
            os.makedirs(outdir) # might not be there yet...
        except:
            pass
    else:
        outdir = tempfile.mkdtemp(prefix=title)
    if type(rcmd) == type([]):
        script = '\n'.join(rcmd)
    else: # string
        script = rcmd
    sto = file(stoname,'w')
    rscriptname = os.path.join(outdir,'Runme.R')
    print 'rscriptname = ',rscriptname
    rscript = file(rscriptname,'w')
    rscript.write(script)
    rscript.write('\n#R script autogenerated by rgenetics/rgutils.py on %s\n' % timenow())
    rscript.close()
    vcl = '%s --slave --vanilla < %s' %  (rexe,rscriptname)
    x = subprocess.Popen(vcl,shell=True,stderr=sto,stdout=sto,cwd=outdir)
    retval = x.wait()
    sto.close()
    rlog = file(stoname,'r').readlines()
    if outdir <> None:
        flist = os.listdir(outdir)
    else:
        flist = os.listdir('.')
    flist.sort
    flist = [(x,x) for x in flist] 
    for i,x in enumerate(flist):
        if x == rname:
            flist[i] = (x,'R script for %s' % title)
        elif x == stoname:
            flist[i] = (x,'R log for %s' % title)  
    if False and not outdir:
	os.unlink(outdir) 
    return rlog,flist # for html layout
 
def runPlink(bfn='bar',ofn='foo',logf='x.log',plinktasks=[],cd='./',vclbase = []):
    """run a series of plink tasks and append log results to stdout
    vcl has a list of parameters for the spawnv
    common settings can all go in the vclbase list and are added to each plinktask
    """    
    # root for all
    fplog,plog = tempfile.mkstemp()
    mylog = file(logf,'a+')
    mylog.write('## Rgenetics: http://rgenetics.org Galaxy Tools rgQC.py Plink runner\n')
    for task in plinktasks: # each is a list
        vcl = vclbase + task
        sto = file(plog,'w')
        x = subprocess.Popen(' '.join(vcl),shell=True,stdout=sto,stderr=sto,cwd=cd)
        retval = x.wait()
        sto.close()
        try:
            lplog = file(plog,'r').read()
            mylog.write(lplog)
            os.unlink(plog) # no longer needed
        except:
            mylog.write('### %s Strange - no std out from plink when running command line\n%s' % (timenow(),' '.join(vcl)))
    mylog.close()

def pruneLD(plinktasks=[],cd='./',vclbase = []):
    """
    plink blathers when doing pruning - ignore
    Linkage disequilibrium based SNP pruning
    if a million snps in 3 billion base pairs, have mean 3k spacing
    assume 40-60k of ld in ceu, a window of 120k width is about 40 snps
    so lots more is perhaps less efficient - each window computational cost is
    ON^2 unless the code is smart enough to avoid unecessary computation where
    allele frequencies make it impossible to see ld > the r^2 cutoff threshold
    So, do a window and move forward 20? 
    The fine Plink docs at http://pngu.mgh.harvard.edu/~purcell/plink/summary.shtml#prune 
    reproduced below
    
Sometimes it is useful to generate a pruned subset of SNPs that are in approximate linkage equilibrium with each other. This can be achieved via two commands: --indep which prunes based on the variance inflation factor (VIF), which recursively removes SNPs within a sliding window; second, --indep-pairwise which is similar, except it is based only on pairwise genotypic correlation.

Hint The output of either of these commands is two lists of SNPs: those that are pruned out and those that are not. A separate command using the --extract or --exclude option is necessary to actually perform the pruning.

The VIF pruning routine is performed:
plink --file data --indep 50 5 2

will create files

     plink.prune.in
     plink.prune.out

Each is a simlpe list of SNP IDs; both these files can subsequently be specified as the argument for 
a --extract or --exclude command.

The parameters for --indep are: window size in SNPs (e.g. 50), the number of SNPs to shift the 
window at each step (e.g. 5), the VIF threshold. The VIF is 1/(1-R^2) where R^2 is the multiple correlation coefficient for a SNP being regressed on all other SNPs simultaneously. That is, this considers the correlations between SNPs but also between linear combinations of SNPs. A VIF of 10 is often taken to represent near collinearity problems in standard multiple regression analyses (i.e. implies R^2 of 0.9). A VIF of 1 would imply that the SNP is completely independent of all other SNPs. Practically, values between 1.5 and 2 should probably be used; particularly in small samples, if this threshold is too low and/or the window size is too large, too many SNPs may be removed.

The second procedure is performed:
plink --file data --indep-pairwise 50 5 0.5

This generates the same output files as the first version; the only difference is that a 
simple pairwise threshold is used. The first two parameters (50 and 5) are the same as above (window size and step); the third parameter represents the r^2 threshold. Note: this represents the pairwise SNP-SNP metric now, not the multiple correlation coefficient; also note, this is based on the genotypic correlation, i.e. it does not involve phasing.

To give a concrete example: the command above that specifies 50 5 0.5 would a) consider a
window of 50 SNPs, b) calculate LD between each pair of SNPs in the window, b) remove one of a pair of SNPs if the LD is greater than 0.5, c) shift the window 5 SNPs forward and repeat the procedure.

To make a new, pruned file, then use something like (in this example, we also convert the 
standard PED fileset to a binary one):
plink --file data --extract plink.prune.in --make-bed --out pruneddata
    """
    fplog,plog = tempfile.mkstemp()
    alog = []
    alog.append('## Rgenetics: http://rgenetics.org Galaxy Tools rgQC.py Plink pruneLD runner\n')
    for task in plinktasks: # each is a list
        vcl = vclbase + task
        sto = file(plog,'w')
        x = subprocess.Popen(' '.join(vcl),shell=True,stdout=sto,stderr=sto,cwd=cd)
        retval = x.wait()
        sto.close()
        try:
            lplog = file(plog,'r').readlines()
            lplog = [x for x in lplog if x.find('Pruning SNP') == -1]
            alog += lplog
            alog.append('\n')
            os.unlink(plog) # no longer needed
        except:
            alog.append('### %s Strange - no std out from plink when running command line\n%s\n' % (timenow(),' '.join(vcl)))
    return alog
 
