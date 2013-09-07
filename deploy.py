import sys
import os
 
import urllib
import urllib2
import tarfile
import shutil
 
 
APP_NAME="wordpress"
DEPLOY_DIR = "/var/www/releases"
DOWNLOAD_DIR = "/var/www/download"
URL_LASTVER = "http://127.0.0.1/deploy/lastver"
URL_LIVEVER = "http://127.0.0.1/deploy/livever"
URL_PKG = "http://127.0.0.1/deploy/package/"
DEPLOY_TOKEEP = 1
 
ROOT_DOC_PATH = "/var/www/html/current"
 
whitelist = []
 
def getURLContent(url):
    return urllib2.urlopen(url).read().strip()
 
def checkLastVersion():
    lastver = getURLContent(URL_LASTVER)
    whitelist.append(lastver)
    pkg_path = os.path.join(DOWNLOAD_DIR,'%s-%s.tgz' % (APP_NAME, lastver))
    deploy_path = os.path.join(DEPLOY_DIR,'%s-%s' % (APP_NAME, lastver))
    if not os.path.exists(pkg_path):
        if not download_pkg(lastver):
            return False
    if not os.path.exists(deploy_path):
        deploy_pkg(pkg_path, DEPLOY_DIR)
 
def download_pkg(ver):
    pkg_name = '%s-%s.tgz' % (APP_NAME, ver)
    pkg_md5sum = pkg_name + '.md5'
    pkg_url = URL_PKG + pkg_name
    pkg_md5sum_url = URL_PKG + pkg_md5sum
    pkg_path = os.path.join(DOWNLOAD_DIR, pkg_name)
    with open(pkg_path,'wb') as fd:
        print "DL:", pkg_name
        fd.write(urllib2.urlopen(pkg_url).read())
    md5sum = getURLContent(pkg_md5sum_url)
    if not checkFileSum(pkg_path, md5sum):
        return False 
    return True
 
def checkFileSum(path, sum):
    with open(path) as fd:
        import hashlib
        md5 = hashlib.md5(fd.read()).hexdigest()
        if md5 == sum:
            return True
        else:
            return False
 
def deploy_pkg(pkg, deploy_dir):
    tar = tarfile.open(pkg, 'r:gz')
    tar.extractall(path=deploy_dir)
 
def checkLiveVersion():
    livever = getURLContent(URL_LIVEVER)
    whitelist.append(livever)
    deploy_path = os.path.join(DEPLOY_DIR,'%s-%s' % (APP_NAME, livever))
    if os.path.exists(deploy_path):
        if os.path.exists(ROOT_DOC_PATH):
            current_target = os.readlink(ROOT_DOC_PATH)
            if current_target != deploy_path:
                print "Switch live: %s -> %s" % (ROOT_DOC_PATH, deploy_path)
                os.unlink(ROOT_DOC_PATH)
                os.symlink(deploy_path, ROOT_DOC_PATH)
        else:
            print "Create live: %s -> %s" % (ROOT_DOC_PATH, deploy_path)
            os.symlink(deploy_path, ROOT_DOC_PATH)
 
 
def versionSort(l):
    from distutils.version import LooseVersion
    sorted_ver_list = [LooseVersion(y) for y in l if y]
    sorted_ver_list.sort()
    return [i.vstring for i in sorted_ver_list]
 
def clean():
    dirlist = [i.split('-')[1] for i in os.listdir(DEPLOY_DIR)]
    dl_list = [os.path.splitext(i)[0].split('-')[1] for i in os.listdir(DOWNLOAD_DIR)]
    deploy_vs = versionSort(dirlist)
    dl_vs = versionSort(dl_list)
    deploy_tobe_deleted = ['%s-%s' % (APP_NAME, i) for i in deploy_vs[:-DEPLOY_TOKEEP] if i not in whitelist ]
    dl_tobe_deleted = ['%s-%s.tgz' % (APP_NAME, i) for i in dl_vs[:-DEPLOY_TOKEEP] if i not in whitelist]
    for d in deploy_tobe_deleted:
        p = os.path.join(DEPLOY_DIR,d)
        print "clean:", p 
        shutil.rmtree(p)
    for p in dl_tobe_deleted:
        dp = os.path.join(DOWNLOAD_DIR, p)
        print "clean:", dp 
        os.remove(dp)
 
def file_lock(lock_file):
    if os.path.exists(lock_file):
        print "Already running"
        sys.exit(-1)
    else:
        with open(lock_file,'w') as fd:
            fd.write('1')
 
def file_unlock(lock_file):
    if os.path.exists(lock_file):
        os.remove(lock_file)
 
def main():
    file_lock('/tmp/deploy')
    checkLastVersion()
    checkLiveVersion()
    clean()
    file_unlock('/tmp/deploy')
 
if __name__ == "__main__":
    main()
