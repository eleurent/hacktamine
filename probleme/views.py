from django.shortcuts import render_to_response, get_object_or_404, redirect
from probleme.models import Probleme, Solution, Duel
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required
import subprocess

@login_required
# Le probleme en cours
def submit(request):
    probleme = request.user.get_profile().probleme()
    if not probleme:
        return HttpResponseRedirect('/dashboard/')
    if request.POST:
        solution = Solution.objects.create(probleme = probleme, source = request.POST['source'], user = request.user, status='idle')
        solution.enregistrer()
        solution.changer_status('compiling')
        rc = solution.compiler()
        if rc == 0:
            solution.changer_status('running')
            output = solution.tester()
            if solution.status == 'valid':
                solution.probleme.reussi.add(request.user)
        else:
            solution.changer_status('compiling-error')  
            output = "ERREUR DE COMPILATION"
        # return render_to_response('probleme/submit.html', {'probleme':probleme, 'solution':solution, 'output':output},context_instance=RequestContext(request))
        return HttpResponseRedirect('/dashboard/')
    else:
        last_solution = Solution.objects.filter(probleme = probleme, user = request.user)
        if last_solution:
            last_solution = last_solution[0]
        return render_to_response('probleme/submit.html', {'probleme':probleme, 'last_solution':last_solution},context_instance=RequestContext(request))
        
# Tableau de bord
def dashboard(request):
    if Duel.objects.count() > 0:
        duel = Duel.objects.all()[0]
        solutions_joueur1_list = Solution.objects.filter(user = duel.joueur1)
        solutions_joueur2_list = Solution.objects.filter(user = duel.joueur2)
        return render_to_response('probleme/duel.html', {'duel':duel, 'solutions_joueur1_list':solutions_joueur1_list, 'solutions_joueur2_list':solutions_joueur2_list},context_instance=RequestContext(request))
    else:
        solutions_list = Solution.objects.all()
        return render_to_response('probleme/dashboard.html', {'solutions_list':solutions_list},context_instance=RequestContext(request))