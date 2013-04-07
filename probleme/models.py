#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
import subprocess, threading
import re
import time

# Create your models here.
class Probleme(models.Model):
    enonce = models.TextField()
    difficulte = models.IntegerField()
    reussi = models.ManyToManyField(User, blank=True, null=True)
    
    class Meta:
        ordering = ['difficulte']
    
    def __unicode__(self):
        return self.enonce
    
    def numero(self):
        return Probleme.objects.filter(difficulte__lte = self.difficulte).count()

class Duel(models.Model):
    problemes = models.ManyToManyField(Probleme)
    joueur1 = models.ForeignKey(User, related_name = "duel_joueur1")
    joueur2 = models.ForeignKey(User, related_name = "duel_joueur2")
    
    def __unicode__(self):
        return str(self.joueur1) + " VS " + str(self.joueur2)
        
class Solution(models.Model):
    STATUSCHOICE = (
        ('idle', 'En attente'),
        ('compiling', 'Compilation...'),
        ('compiling-error', 'Erreur de compilation'),
        ('running', 'En cours d\'execution...'),
        ('running-error', 'Erreur d\'execution'),
        ('bad-output', 'Mauvais résultat'),
        ('timeout', 'Temps dépassé'),
        ('valid', 'Valide'),
    )

    probleme = models.ForeignKey(Probleme)
    source = models.TextField()
    user = models.ForeignKey(User)
    date = models.DateTimeField(default=datetime.now, blank=True)
    status = models.CharField(max_length=32)
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        return str(self.user) + ' -> ' + str(self.probleme.numero())
    
    def filename(self):
        return str(self.user.username)+str(self.date.hour)+str(self.date.minute)+str(self.date.second)
    
    def main_class_name(self):
        return re.findall(r"class\s+([\w]*)\s+\{", self.source)
        
    def changer_status(self, status):
        self.status = status
        self.save()
        
    def enregistrer(self):
        file=open('%s.java' % (self.filename()),'w+')
        file.write(self.source)
        file.close();
        
    def compiler(self):
        ccmd = ['javac', self.filename()+'.java']
        process = subprocess.Popen(ccmd)
        process.wait()        
        return process.returncode
        
    # def executer(self, args):
        # rcmd = ['java', self.main_class_name()]
        # output = ""
        # process = subprocess.Popen(rcmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        # process.stdin.write(args)
        # output = process.communicate()[0]    
        # return process.returncode, output
        
    def executer(self, args):
        class_names = self.main_class_name()
        main_class=""
        if class_names:
            main_class = class_names[-1]
        command = Command("java " + main_class, self)       
        rc, output = command.run(timeout=10, args=args)
        return rc, output
    
    def tester(self):
        tests = self.probleme.test_set.all()
        for (numero, test) in enumerate(tests):
            rc, output = self.executer(test.input)
            output = output.rstrip()
            if self.status == 'timeout':
                return "Temps limite atteint au test " + str(numero)
            if rc != 0:
                self.changer_status('running-error')                
                return "Erreur d'execution au test "+ str(numero)
            if output != test.output:
                self.changer_status('bad-result')                
                return "Mauvais resultat au test " + str(numero) + " " + output + "!=" + test.output
        self.changer_status('valid')
        return "Programme valide"

class Test(models.Model):
    probleme = models.ForeignKey(Probleme)
    input = models.TextField()
    output = models.TextField()
    
    def __unicode__(self):
        return str(self.input) + ' -> ' + str(self.probleme.numero())
        
class Command(object):
    def __init__(self, cmd, solution):
        self.solution = solution
        self.cmd = cmd
        self.process = None
        self.output = ""

    def run(self, timeout, args):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            self.process.stdin.write(args)
            self.output = self.process.communicate()[0]
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.solution.changer_status('timeout')
            self.process.terminate()
            thread.join()        
        return self.process.returncode, self.output