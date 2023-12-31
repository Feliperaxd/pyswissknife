import json
from pathlib import Path
import functools, inspect, time, warnings
from typing import Any, Callable, Dict, Optional, Union


class TimeTracker:


    def __init__(
        self: 'TimeTracker',
        name: str
    ) -> None:
        
        """
        This class is a useful tool for measuring how long 
        it takes for a specific task to execute in Python!

        Args:
            - name (str): Name or ID for this tracker! 

        Attributes:
            - name (str): Name or ID for this tracker!
            - is_running (bool): 'False' the timer has stopped, 'True' it's running!
            - elapsed_time (float): The time from start to stop, excluding intervals between
              stops and starts!
            - total_elapsed_time (float): The time from the initial start to the final stop,
              without excluding any stops!
            - track_log (Dict): Used to store tracker data!
                - start: Stores all start markers.
                - stop: Stores all stop markers.
                - blocked: Stores all blocked actions in the sequence of location, line, and reason.
            - file_name (str): Name of the file where the data will be saved!
        """

        self.name = name
        self.is_running = False
        self.elapsed_time = None
        self.total_elapsed_time = None
        self.track_log: Dict = {
            'start': [],
            'stop': [],
            'blocked': []
        }
        self.file_name: str = f'chronodata_{self.name}.json'

    def _bug_blocker(
        function: Callable[['TimeTracker'], Any]
    ) -> Callable[['TimeTracker'], Any]:
        
        """
        This is a private decorator, use it only to prevent and block possible problems 
        in functions!
        """

        def _save_block_log(
            self: 'TimeTracker',
            line: int,
            local: Union[Path, str],
            reason: str
        ) -> None:
            
            """
            Use this to block and save to log!

            Args:
                - self: The class instance!
                - line (int): Line where the action was blocked!
                - local (Union[Path, str]): Local where the action was blocked!
                - reason (str): Reason for blocking the action!
            """

            warnings.warn_explicit(
                message=f'Blocked: {function.__qualname__}; {reason}',
                category=UserWarning,
                filename=local,
                lineno=line
            )
            self.track_log['blocked'].append(
                (
                    local, 
                    line,
                    f'Blocked: {function.__qualname__}; {reason}'
                )
            )

        @functools.wraps(function)
        def wrapper(
            self: 'TimeTracker',
            *args,
            **kwargs
        ) -> Any:
               
            frame_info = inspect.getframeinfo(
                inspect.currentframe().f_back
            )
            if function.__name__ == 'start':
                if self.is_running:
                    _save_block_log(
                        self=self,
                        line=frame_info[1],
                        local=frame_info[0],
                        reason='Double call!'    
                    )
                else:
                    self.is_running = True
                    return function(self, *args, **kwargs)

            elif function.__name__ == 'stop':
                if not self.is_running:
                    _save_block_log(
                        self=self,
                        line=frame_info[1],
                        local=frame_info[0],
                        reason='Double call!'    
                    )
                else:
                    self.is_running = False
                    return function(self, *args, **kwargs)
            
            elif function.__name__ == 'get_elapsed_time':
                if not self.track_log['start']:
                    _save_block_log(
                        self=self,
                        line=frame_info[1],
                        local=frame_info[0],
                        reason="The tracker hasn't started yet!"    
                    )
                    return None
                elif not self.track_log['stop']:
                    _save_block_log(
                        self=self,
                        line=frame_info[1],
                        local=frame_info[0],
                        reason="The tracker hasn't been completed yet!"
                    )
                    return None
                elif self.is_running:
                    warnings.warn(
                        message='Opened tracker. Only closed trackers will be calculated.',
                        category=UserWarning
                    )
                    return function(self, *args, **kwargs)
                else:
                    return function(self, *args, **kwargs)
                
        return wrapper

    @_bug_blocker
    def start(
        self: 'TimeTracker'
    ) -> float:
        
        """
        Start the timer!

        Args:
            - self: The class instance!
        
        Returns:
            - float: Time when the chronometer started!
        """

        start_time = time.perf_counter()
        self.track_log['start'].append(start_time)
        
        return start_time
    
    @_bug_blocker
    def stop(
        self: 'TimeTracker'
    ) -> float:
        
        """
        Stop or pause the timer!

        Args:
            - self: The class instance!
        
        Returns:
            - float: Time when the chronometer stoped!
        """

        stop_time = time.perf_counter()
        self.track_log['stop'].append(stop_time)

        return stop_time           

    @_bug_blocker
    def get_elapsed_time(
        self: 'TimeTracker'
    ) -> Union[float, None]:
        
        """
        Calculates and obtains the elapsed time!

        Args:
            - self: The class instance!
        
        Returns:
            - float: The time from start to stop, excluding intervals between stops and 
            starts!
        """

        self.total_elapsed_time = (
            self.track_log['stop'][-1] - 
            self.track_log['start'][0]
        ) 
        if self.elapsed_time is None:
            _elapsed_time = 0
            
        start_log = self.track_log['start']
        stop_log = self.track_log['stop']
        
        if self.is_running:
            start_log.pop()

        for start, stop in zip(start_log, stop_log):        
            _elapsed_time += stop - start
        
        self.elapsed_time = _elapsed_time
        return self.elapsed_time
    
    def save(
        self: 'TimeTracker',
        dir_path: Optional[Union[Path, str]] = None
    ) -> None:
        
        data = {
            'name': self.name,
            'is_running': self.is_running,
            'elapsed_time': self.elapsed_time,
            'total_elapsed_time': self.total_elapsed_time,
            'log': self.track_log
        }
        
        if dir_path is None: dir_path = self.file_name
        else: dir_path = Path(dir_path) / self.file_name
        
        with open(dir_path, 'w+') as file:
            json.dump(data, file)

    def load(
        self: 'TimeTracker',
        dir_path: Optional[Union[Path, str]] = None
    ) -> None:
        
        if dir_path is None: dir_path = self.file_name
        else: dir_path = Path(dir_path) / self.file_name

        with open(dir_path, 'r') as file:
            data = json.load(file)
        
        self.name = data['name']
        self.is_running = data['is_running']
        self.elapsed_time = data['elapsed_time']
        self.total_elapsed_time = data['total_elapsed_time']
        self.track_log = data['log']
        


class ExecutionTimeTracker(TimeTracker):


    def __init__(
        self: 'ExecutionTimeTracker',
        function: Callable[[Any], Any]
    ) -> None:
        
        """
        A class to time the execution of a provided function!
        To use this class, decorate your function with it!

        Args:
            - function (callable): The function to be timed.
            
        Attributes:
            - function (callable): The function to be timed.
            - exec_start_time (float or None): Start time of the function execution.
            - exec_end_time (float or None): End time of the function execution.
            - exec_elapsed_time (float or None): Elapsed time taken by the function.
        """
        
        self.function = function
        super().__init__(
            name=function.__qualname__
        )

    def __call__(
        self: 'ExecutionTimeTracker', 
        *args: Any, 
        **kwargs: Any
    ) -> Any:
        
        self.start()
        self.func_out = self.function(
            *args, **kwargs
        )
        self.stop()    
    
        return self.func_out

b = TimeTracker('aasdsd')
b.start()

time.sleep(1)

b.stop()
print(b.get_elapsed_time())
