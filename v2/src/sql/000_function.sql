-- Source for calculations: https://en.wikipedia.org/wiki/Rotation_of_axes
-- Basic idea: rotate the startline to a vertical line, and use the same rotation on the boats' coordinates. 
-- The y coordinate is then the relative start position (between 0 and 1). 

--IF OBJECT_ID(N'powertracks.FindOrthPosOnLine', N'FN') IS NOT NULL 
--    DROP FUNCTION powertracks.FindOrthPosOnLine ;
--GO

-- Use float instead of decimals, in order to prevent underfloat (and divide by zeroes). 
CREATE FUNCTION powertracks.FindOrthPosOnLine(@l1x float, @l1y float, @l2x float, @l2y float, @px float, @py float)
  RETURNS DECIMAL(9,3)
  AS
  BEGIN
    DECLARE @r as float; 
    DECLARE @theta as float; 
    DECLARE @translated_px as float; 
    DECLARE @translated_py as float; 
    DECLARE @rotated_py AS DECIMAL(9,5); 

    SET @r = sqrt( power(@l2x-@l1x, 2) + power(@l2y-@l1y, 2) );
    SET @theta = -atan( (@l2x - @l1x) / ( @l2y - @l1y) );

    SET @translated_px = @px - @l1x; 
    SET @translated_py = @py - @l1y; 

    SET @rotated_py = (-@translated_px * sin(@theta) + @translated_py * cos(@theta)) / @r; 

    IF @l2y < @l1y
      SET @rotated_py= - @rotated_py;
    
    RETURN 1 - @rotated_py; 
    
  END;

CREATE FUNCTION powertracks.GetSmallest
(
    -- Add the parameters for the function here
    @val1 int,  @val2 int,  @val3 int
)
RETURNS int
AS
BEGIN
Declare @result int
set @result = case when @val1 < @val2 then
               case when @val1 < @val3 then 
                @val1
               else
                @val3
               end
        when @val2 < @val3 then 
                @val2
        else
                 @val3
    end
  return @result  
END 


CREATE FUNCTION powertracks.FindAngle(
    @deg1 int,  @deg2 int
)
RETURNS int
AS
BEGIN
    declare @angle1 int
    declare @angle2 int
    declare @angle3 int
    declare @result int

    set @angle1 = abs(@deg1 - @deg2) 
    set @angle2 = abs(@deg1 + 360 - @deg2) 
    set @angle3 = abs(@deg1 - 360 - @deg2) 

    set @result = case when @angle1 < @angle2 then 
                            case when @angle1 < @angle3 then @angle1 else @angle3 end 
                       else 
                            case when @angle2 < @angle3 then @angle2 else @angle3 end 
                        end 

    return @result  
END 
GO
