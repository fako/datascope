from django.shortcuts import HttpResponse, render_to_response

from sources.management.commands.acteurs_spot import Command as ActeursSpotCommand
from sources.management.commands.moeder_anne_casting import Command as MoederAnneCommand

from pandas import DataFrame


def casting_comparison_by_face(request):
    moeder_anne = DataFrame.from_records(
        MoederAnneCommand.extract(limit=0)
    )
    acteurs_spot = DataFrame.from_records(
        ActeursSpotCommand.extract(limit=0)
    )
    data = moeder_anne.merge(acteurs_spot, on="voornaam", how="left").dropna(subset=["achternaam"])
    #return HttpResponse(data.to_json(orient="records"))
    return render_to_response(
        "birthday_calendar/casting_comparison_by_face.html",
        {"data": data.to_records()}
    )
