from .database import db, Base
import json
from core.ffk import Flag
from core.workflow import Workflow

class Triggers(Base):
    __tablename__ = "triggers"
    name = db.Column(db.String(255), nullable=False)
    play = db.Column(db.String(255), nullable=False)
    condition = db.Column(db.String(255, convert_unicode=False), nullable=False)

    def __init__(self, name, play, condition):
        self.name = name
        self.play = play
        self.condition = condition

    def edit_trigger(self, form=None):
        if form:
            if form.name.data:
                self.name = form.name.data

            if form.play.data:
                self.play = form.play.data

            if form.conditional.data:
                self.condition = str(form.conditional.data)

        return True

    def as_json(self):
        return {'name': self.name,
                'conditions': self.condition,
                'play': self.play}

    @staticmethod
    def execute(data_in):
        triggers = Triggers.query.all()
        listener_output = {}
        for trigger in triggers:
            conditionals = json.loads(trigger.condition)
            if all(Triggers.__execute_trigger(conditional, data_in) for conditional in conditionals):
                workflow_to_be_executed = Workflow.get_workflow(trigger.play)
                if workflow_to_be_executed:
                    trigger_results = workflow_to_be_executed.execute()
                else:
                    return json.dumps({"status": "trigger error: play could not be found"})
                listener_output[trigger.name] = json.loads(str(trigger_results[0]))
        return listener_output

    @staticmethod
    def __execute_trigger(conditional, data_in):
        conditional = json.loads(conditional)
        return Flag(**conditional)(data_in)

    def __repr__(self):
        return json.dumps(self.as_json())

    def __str__(self):
        out = {'name': self.name,
               'conditions': json.loads(self.condition),
               'play': self.play}
        return json.dumps(out)
